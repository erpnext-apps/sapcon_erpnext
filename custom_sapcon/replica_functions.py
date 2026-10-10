import frappe

@frappe.whitelist()
@frappe.read_only()
def db_sql_qry(qry,values,as_dict):
    data = frappe.db.sql(qry,values=values,as_dict=as_dict)
    return data

#Example to Use this for replica server
#temp = frappe.call(method="sapcon_erpnext.custom_sapcon.replica_functions.db_sql_qry",qry = qry,values={},as_dict=1)

@frappe.whitelist()
@frappe.read_only()
def db_get_value(doctype,docname,fieldname):
    field_value = frappe.db.get_value(doctype,docname,fieldname)
    return field_value
#Example to Use this for replica server
#temp = frappe.call(method="sapcon_erpnext.custom_sapcon.replica_functions.db_get_value",doctype='Quality Procedure',docname="QP-2026-00001",fieldname='creation')

@frappe.whitelist()
@frappe.read_only()
def get_doc(doctype,docname):
    doc = frappe.db.get_doc(doctype,docname)
    return doc
#Example to Use this for replica server
#temp = frappe.call(method="sapcon_erpnext.custom_sapcon.replica_functions.get_doc",doctype='Quality Procedure',docname="QP-2026-00001")

