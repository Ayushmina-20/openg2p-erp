from odoo import models
from odoo.exceptions import UserError, ValidationError, _logger

AVAILABLE_PRIORITIES = [("0", "Urgent"), ("1", "High"), ("2", "Normal"), ("3", "Low")]


class RegistrationService(models.Model):
    _inherit = ["openg2p.registration"]

    def post_auth_find_duplicate_beneficiary(self, auth_id, auth_id_type):
        type_code_id = self.env["openg2p.beneficiary.id_category"].search(
            [("code", "=", auth_id_type)], limit=1).id
        kycdup_list = (self.env["openg2p.beneficiary.id_number"].search(
            [("name", "=", auth_id), ("category_id", "=", type_code_id)]))
        _logger.info(f"auth_id : {auth_id}. Post Auth. Size of duplicates: {kycdup_list}")
        return kycdup_list

    def create_registration_for_single_submission(self,regd, odk_data):
        #self.create_registration(regd,odk_data)
        current_program_id = int(
            odk_data["program_ids"][len(odk_data["program_ids"]) - 1]
        )
        program_obj = self.env["openg2p.program"].search(
            [("id", "=", current_program_id)]
        )
        autodedup_field = program_obj.autodedup_field
        action = program_obj.action
        stage_name = program_obj.stage_name


        # if os.getenv("SHOULD_DEMO_AUTH", "true").lower() == "true":
        #     demo_auth_res = self.demo_auth(temp)
        # kyc_id is identity number and category type is kyc_type id number
        #kyc_id is identity number and category type is kyc_type id number
        auth_response={"authId":regd["kyc_id"],"authIdType":"KYC_TYPE"}
        if autodedup_field == "kyc":
            kycdup_list = self.post_auth_find_duplicate_beneficiary(
                self,regd["kyc_id"],"KYC_TYPE")
            if len(kycdup_list.ids) != 0:
                if action == "merge":
                    # merging the existing ones with new one and passing the existing_id and current_id as arguments
                    self.merge_registrations(regd, kycdup_list.ids[0])
                elif action == "del_old":
                    # deleting the old registration
                    duplicate_kyc =kycdup_list
                    duplicate_kyc.active = False
                    # deleting the old beneficiary
                    duplicate_kyc_bene = kycdup_list.beneficiary_id

                    duplicate_kyc_bene.active = False
                    # creating registration for new record
                    self.create_registration(regd,odk_data,auth_response)
                elif action == "del_new":
                    print("kyc and delete new")
                    # deleting the current record
            else:
                self.create_registration(regd,odk_data,auth_response)
        elif autodedup_field == "ext_id":
            externaldup_list = (
            self.env["openg2p.registration"]
                .search([("external_id", "=", regd["external_id"])])
                .ids
        )
        if len(externaldup_list) != 0:
            if action == "merge":
                # merging the existing ones with new one and passing the existing_id and current_id as arguments
                self.merge_registrations(regd, externaldup_list[0])
            elif action == "del_old":
                # deleting the old registration
                duplicate_external = self.env["openg2p.registration"].search(
                    [("external_id", "=", regd["external_id"])]
                )
                duplicate_external.active = False
                # deleting the old beneficiary
                duplicate_external_bene = self.env["openg2p.beneficiary"].search(
                    [("external_id", "=", regd["external_id"])]
                )
                duplicate_external_bene.active = False
                # creating registration for new record
                self.create_registration(regd,odk_data,stage_name,auth_response)
            elif action == "del_new":
                print("External id & delete new")
            else:
                self.create_registration(regd,odk_data,stage_name,auth_response)

        else:
            self.create_registration(regd,odk_data,stage_name,auth_response)


    def create_disbursement_fields(self, rid, temp, regd,auth_response):
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
                if (
                    k
                    in [
                        "Status",
                        "AttachmentsExpected",
                        "AttachmentsPresent",
                        "SubmitterName",
                        "SubmitterID",
                        "KEY",
                        "meta-instanceID",
                        "__version__",
                        "bank_name",
                        "city",
                        "district",
                        "chiefdom",
                        "region",
                    ]
                    or k.startswith("_")
                ):
                    continue
                if k == "bank_account_number":
                    if len(str(v) or "") != 0:
                        data["bank_account_number"] = str(v)
                        res = self.env["res.partner.bank"].search(
                            [("acc_number", "=", str(v))]
                        )
                        if res:
                            raise Exception("Duplicate Bank Account Number!")
                        if not res:
                            bank_id = self.env["res.bank"].search(
                                [("name", "=", odk_data["bank_name"])], limit=1
                            )
                            if len(bank_id) == 0:
                                bank_id = self.env["res.bank"].create(
                                    {
                                        "execute_method": "manual",
                                        "name": odk_data["bank_name"],
                                        "type": "normal",
                                    }
                                )
                            else:
                                bank_id = bank_id[0]
                            res = self.env["res.partner.bank"].create(
                                {
                                    "bank_id": bank_id.id,
                                    "acc_number": str(v),
                                    "payment_mode": "AFM",
                                    "bank_name": odk_data["bank_name"],
                                    "acc_holder_name": odk_data["name"],
                                    "partner_id": self.env.ref("base.main_partner").id,
                                }
                            )
                        data["bank_account_id"] = res.id
                elif hasattr(self, k):
                    if k == "partner_id":
                        res = self.env["res.partner"].search(
                            [("partner_id", "=", v)], limit=1
                        )
                        if res:
                            data[k] = res.id
                    elif k == "registered_date":
                        data["registered_date"] = datetime.strptime(v, format)
                    elif k == "categ_ids":
                        res = self.env["categ_ids"].search(
                            [("categ_ids", "=", v)], limit=1
                        )
                        if res:
                            data["categ_ids"] = res.ids
                    elif k == "company_id":
                        res = self.env["company_id"].search(
                            [("company_id", "=", v)], limit=1
                        )
                        if res:
                            data["company_id"] = res.id
                    elif k == "user_id":
                        res = self.env["user_id"].search([("user_id", "=", v)], limit=1)
                        if res:
                            data["user_id"] = res.id
                    elif k == "priority":
                        if v in [i[0] for i in AVAILABLE_PRIORITIES]:
                            data["priority"] = v
                    elif k == "beneficiary_id":
                        res = self.env["openg2p.beneficiary"].search(
                            [("beneficiary_id", "=", rid)], limit=1
                        )
                        if res:
                            data["beneficiary_id"] = res.id
                    elif k == "identities":
                        for vi in v:
                            self.env["openg2p.registration.identity"].create(
                                {
                                    "name": list(vi.keys())[0],
                                    "type": list(vi.values())[0],
                                    "registration_id": rid,
                                }
                            )
                        res = self.env["openg2p.registration.identity"].search(
                            [("registration_id", "=", rid)]
                        )
                        if res:
                            data["identities"] = res.ids
                    elif k == "state_id":
                        state = self.env["res.country.state"].search([("name", "=", v)])
                        if state:
                            data["state_id"] = state.id
                    else:
                        if k == "name":
                            if v is None:
                                continue
                            name_parts = v.split(" ")
                            data["firstname"] = name_parts[0]
                            if len(name_parts) > 1:
                                data["lastname"] = " ".join(name_parts[1:])
                        else:
                            data.update({k: v})
                else:
                    org_data.update({k: v})
            except Exception as e:
                _logger.error(e)

        for k, v in org_data.items():
            try:
                self.env["openg2p.registration.orgmap"].create(
                    {
                        "field_name": k,
                        "field_value": str(v) if v else "",
                        "regd_id": rid,
                    }
                )
            except BaseException as e:
                _logger.error(e)

        try:
            regd.write(data)
            # Updating Program for Registration
            regd.program_ids = [(6, 0, temp["program_ids"])]
            regd.post_auth_create_id(auth_response)
            if temp["stage_id"] == 6:
                regd.create_beneficiary_from_registration()

        except BaseException as e:
            print(e)

        return regd

    def create_registration(self,data,temp,stage_name,auth_response):

        try:
            data["stage_id"]=stage_name
            regd=self.create(data)
            rid = regd.id
            self.create_disbursement_fields(rid, temp, regd,auth_response)
        except BaseException as e:
            _logger.error(e)
            return None

        return regd

    def merge_registrations(self, temp, old_id):
        # Browsing that existing beneficiary
        # existing_registration = self.env["openg2p.registration"].search([("id","=",int(old_id))])
        existing_registration = self.env["openg2p.registration"].browse(old_id)

        # Fields to be merged
        overwrite_data = {
            "street": (temp["chiefdom"] if "chiefdom" in temp.keys() else "-"),
            "street2": (temp["district"] if "district" in temp.keys() else "-")
                       + ", "
                       + (temp["region"] if "region" in temp.keys() else "-"),
            "city": (
                    (temp["city"] if "city" in temp.keys() else "Freetown") or "Freetown"
            ),
            "phone": temp["phone"] or None,

            "external_id": temp["external_id"] or None,
        }

        # Removing None fields
        cleaned_overwrite_data = self.del_none(overwrite_data)

        # Merging specfic fields to beneficiary
        existing_registration.write(cleaned_overwrite_data)

    def post_auth_create_id(self, response):
        return self.env["openg2p.registration.identity"].create({
            "name": response["authId"],
            "type": response["authIdType"],
            "registration_id": self.id
        })
        res = self.env["openg2p.registration.identity"].search(
            [("registration_id", "=", self.id)]
        )
        if res:
            self.write({"identities": res.ids})