from odoo import models
from odoo.exceptions import UserError, ValidationError, _logger
class MappingService(models.Model):
    _name = "mapping.odk_submissions"
    def main_mapping(self,odk_data):
        temp = {}
        self.renaming_submission_data_fields(temp, odk_data)
        from datetime import datetime
        data = {}
        odk_data = temp
        org_data = {}
        format = "%Y-%m-%dT%H:%M:%SZ"
        for k, v in odk_data.items():
            try:
                if k in [
                    "regression_and_progression",
                    "total_quality",
                    "total_equity",
                    "grand_total",
                ]:
                    org_data[k] = v
                    continue
            except Exception as e:
                _logger.error(e)
        return temp

    def renaming_submission_data_fields(self, temp, odk_data):
        odk_map = (
            odk_data["odk_map"]
            if "odk_map" in odk_data.keys()
            else self._get_default_odk_map()
        )

        for k, v in odk_data.items():
            if k.startswith("group"):
                for k2, v2 in v.items():
                    if k2 in odk_map.keys():
                        k2 = odk_map[k2]
                    else:
                        k2 = str(k2).replace("-", "_").lower()
                    if not str(k2).startswith("_"):
                        temp[k2] = v2
            else:
                if not str(k).startswith("_"):
                    temp[str(k).replace("-", "_").lower()] = v

    def _get_default_odk_map(self):
        odk_map_data = {
            "Enter_Today_s_date": "date",
            "Town_Village": "city",
            "Account_Number": "bank_account_number",
            "School_Name": "name",
            "Mobile_Number_of_Respondant": "phone",
        }

        return odk_map_data