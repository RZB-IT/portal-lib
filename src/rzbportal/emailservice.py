import logging
import httpx
import httpcore
from typing import List
from dataclasses import dataclass, Field

logger = logging.getLogger("utils.emailservice")


@dataclass(frozen=True)
class DefaultTemplateParams:
    """
    A class to hold default template parameters for email services.
    Attributes:
        base_url (str): The base URL to be used in email templates.
    """
    base_url: str


class EmailService():
    """EmailService class provides methods to interact with an email service.
    Methods:
        __init__(base_url: str):
            Initializes the EmailService with the base URL of the email service.
        async check_status() -> bool:
        async send_template_email(subject: str, template_id: str, recipients: List[str], template_params: dict | None = None, recipients_overrides: dict | None = None) -> bool:
        _create_body_dict(subject: str, recipients: List[str], template_params: dict | None = None, recipients_overrides: dict | None = None, template_id: str | None = None) -> dict:
    """
    
    def __init__(self, base_url: str, default_template_params: DefaultTemplateParams):
        self._base_url = base_url
        self._default_template_params = default_template_params


    async def check_status(self) -> bool:
        """
        Asynchronously checks the status of the email service.
        Sends a GET request to the email service's status endpoint and returns
        True if the service is reachable and responds with a status code of 200.
        Returns False if there is a connection error.
        Returns:
            bool: True if the email service is reachable and returns status code 200, False otherwise.
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._base_url}/status")
                return response.status_code == 200
        except httpx.ConnectError:
            return False


    async def send_template_email(self, /, subject: str, template_id: str, recipients: List[str], template_params: dict | None = None, recipients_overrides: dict | None = None) -> bool:
        """
        Sends an email using a specified template.
        Args:
            subject (str): The subject of the email.
            template_id (str): The ID of the email template to use.
            recipients (List[str]): A list of recipient email addresses.
            template_params (dict | None, optional): Parameters to be used in the email template. Defaults to None.
            recipients_overrides (dict | None, optional): Overrides for specific recipients. Defaults to None.
        Returns:
            bool: True if the email was successfully sent, False otherwise.
        """
        body = self._create_body_dict(subject, recipients, self._default_template_params, template_params, recipients_overrides, template_id)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(f"{self._base_url}/enqueue", json=body, timeout=30.0)
                return response.status_code == 200
            return True
        except httpx.ConnectError as e:
            logger.error("Connect error")
            return False
        except httpcore.ReadTimeout as e:
            logger.error("Read timeout")
            return False
        except httpx.ReadTimeout as e:
            logger.error("Read timeout")
            return False


    @staticmethod
    def _create_body_dict(
        subject: str,
        recipients: List[str],
        default_template_params: DefaultTemplateParams,
        template_params: dict | None = None,
        recipients_overrides: dict | None = None,
        template_id: str | None = None
    ) -> dict:
        """
        Creates a dictionary representing the body of an email.
        Args:
            subject (str): The subject of the email.
            recipients (List[str]): A list of recipient email addresses.
            template_params (dict, optional): A dictionary of parameters for the email template. Defaults to None.
            recipients_overrides (dict, optional): A dictionary of overrides for individual recipients. Defaults to None.
            template_id (str, optional): The ID of the email template. Defaults to None.
        Returns:
            dict: A dictionary representing the email body.
        Raises:
            ValueError: If no recipients are provided.
        """
        body = dict()
        body["subject"] = subject

        if len(recipients) == 0:
            raise ValueError("No recipients provided")

        body["recipients"] = [{"to": to} for to in recipients]
        
        if template_id is not None:
            body["template_id"] = template_id
            body["template_params"] = template_params if template_params is not None else {}
            body["template_params"].update(
                {"base_url": default_template_params.base_url}
            )

        if recipients_overrides is not None:
            for recipient in body["recipients"]:
                recipient["template_params_overide"] = recipients_overrides.get(recipient["to"], {})

        return body
