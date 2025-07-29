import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LLMProvider(models.Model):
    _name = "llm.provider"
    _description = "LLM Provider"
    _order = "sequence, name"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    provider_type = fields.Selection(
        [
            ("groq", "Groq"),
            ("openai", "OpenAI"),
            ("anthropic", "Anthropic"),
            ("custom", "Custom"),
        ],
        string="Provider Type",
        required=True,
        default="groq",
    )
    api_key = fields.Char(string="API Key", required=True)
    endpoint = fields.Char(
        string="API Endpoint",
        default="https://api.groq.com/openai/v1/chat/completions",
    )
    model_name = fields.Char(
        string="Model Name", 
        default="llama-3.1-70b-versatile",
        help="Model to use for this provider"
    )
    max_tokens = fields.Integer(string="Max Tokens", default=4000)
    temperature = fields.Float(string="Temperature", default=0.1)
    active = fields.Boolean(string="Active", default=True)
    is_default = fields.Boolean(string="Default Provider", default=False)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.model
    def get_default_provider(self):
        """Get the default LLM provider for the current company"""
        provider = self.search([
            ("is_default", "=", True),
            ("active", "=", True),
            ("company_id", "=", self.env.company.id),
        ], limit=1)
        if not provider:
            provider = self.search([
                ("active", "=", True),
                ("company_id", "=", self.env.company.id),
            ], limit=1)
        return provider

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_default"):
                # Ensure only one default provider per company
                existing_default = self.search([
                    ("is_default", "=", True),
                    ("company_id", "=", vals.get("company_id", self.env.company.id)),
                ])
                existing_default.write({"is_default": False})
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("is_default"):
            # Ensure only one default provider per company
            for record in self:
                existing_default = self.search([
                    ("is_default", "=", True),
                    ("company_id", "=", record.company_id.id),
                    ("id", "!=", record.id),
                ])
                existing_default.write({"is_default": False})
        return super().write(vals)

    def _prepare_headers(self):
        """Prepare headers for API request"""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.provider_type == "groq":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.provider_type == "openai":
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.provider_type == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers

    def _prepare_payload(self, prompt, **kwargs):
        """Prepare payload for API request"""
        if self.provider_type in ["groq", "openai"]:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            if kwargs.get("response_format"):
                payload["response_format"] = kwargs["response_format"]
        elif self.provider_type == "anthropic":
            payload = {
                "model": self.model_name,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "messages": [{"role": "user", "content": prompt}],
            }
        else:
            # Custom provider - basic format
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
        
        return payload

    def process_prompt(self, prompt, **kwargs):
        """Process a prompt using the LLM provider"""
        self.ensure_one()
        
        if not self.active:
            return {"success": False, "error": "Provider is not active"}
        
        try:
            headers = self._prepare_headers()
            payload = self._prepare_payload(prompt, **kwargs)
            
            _logger.info(f"Sending request to {self.provider_type} LLM: {self.endpoint}")
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30,
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract content based on provider type
                if self.provider_type in ["groq", "openai"]:
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                elif self.provider_type == "anthropic":
                    content = result.get("content", [{}])[0].get("text", "")
                else:
                    content = result.get("content", result.get("text", ""))
                
                # Try to parse as JSON if response_format is json_object
                if kwargs.get("response_format", {}).get("type") == "json_object":
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        _logger.warning("Failed to parse LLM response as JSON")
                
                return {
                    "success": True,
                    "content": content,
                    "raw_response": result,
                }
            else:
                error_msg = f"LLM API error: {response.status_code} - {response.text}"
                _logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            _logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def test_connection(self):
        """Test the connection to the LLM provider"""
        self.ensure_one()
        
        test_prompt = "Hello, this is a test. Please respond with 'Connection successful'."
        
        result = self.process_prompt(test_prompt, max_tokens=50)
        
        if result.get("success"):
            message = _("Connection successful! Response: %s") % result.get("content", "")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Test"),
                    "message": message,
                    "type": "success",
                },
            }
        else:
            error_msg = result.get("error", "Unknown error")
            raise UserError(_("Connection failed: %s") % error_msg)