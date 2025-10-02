import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetsCrew:
    def __init__(self, spreadsheet_id: str, worksheet_name: str = "Funding Round", credentials_path: str | None = None):
        base_dir = os.path.dirname(__file__)
        cred_path = credentials_path or os.path.join(base_dir, "config", "credentials.json")

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        self.client = gspread.authorize(creds)

        # Abre a planilha por ID e garante a aba
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        try:
            self.sheet = self.spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            self.sheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)

    def append_row(self, row: list):
        self.sheet.append_row(row, value_input_option="USER_ENTERED")

    def append_rows(self, rows: list[list]):
        for row in rows:
            self.append_row(row)

    def save_investors(self, investors, worksheet_name: str = "Investors"):
        try:
            ws = self.spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
            # Adiciona cabeçalho
            ws.append_row(["name", "type", "website", "hq_country", "focus", "portfolio_url"])
        
        for inv in investors:
            row = [
                inv.get("name", ""),
                inv.get("type", ""),
                inv.get("website", ""),
                inv.get("hq_country", ""),
                inv.get("focus", ""),
                inv.get("portfolio_url", "")
            ]
            ws.append_row(row, value_input_option="USER_ENTERED")

    def save_startups(self, startups, vc_name: str, worksheet_name: str = "Startups"):
        try:
            ws = self.spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = self.spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
            # Adiciona cabeçalho
            ws.append_row(["startup_name", "website", "description", "sector", "stage", "vc_name"])
        
        for st in startups:
            row = [
                st.get("name", ""),
                st.get("website", ""),
                st.get("description", ""),  # Você pode mapear de outro campo se necessário
                st.get("sector", ""),
                st.get("stage", ""),  # Você pode mapear de funding ou outro campo
                vc_name
            ]
            ws.append_row(row, value_input_option="USER_ENTERED")