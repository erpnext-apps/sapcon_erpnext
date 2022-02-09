
from heapq import merge
import frappe
import os
from frappe import _

import PyPDF2 

@frappe.whitelist()
def custom_pdf_merge(doctype,docid):

	mergeFile = PyPDF2.PdfFileMerger()	

	final_merged_file = _("Merged_{}.pdf").format(docid)

	#Generate pdf of original record
	doc_pdf = frappe.attach_print(doctype, docid,str(docid), print_format="")
	docfile = open(_("{}.pdf").format(docid),'wb')
	docfile.write(doc_pdf["fcontent"])
	doc_to_merge = PyPDF2.PdfFileReader(_("{}.pdf").format(docid),'rb')
	mergeFile.append(doc_to_merge,'rb')

	#Fetch attachments 
	attached_docs = frappe.get_all("File",
			fields=["name", "file_name", "file_url", "is_private"],
			filters = {"attached_to_name": docid, "attached_to_doctype": doctype, "is_private":0})
	
	file_path = frappe.utils.get_files_path(
				attached_docs[0].file_name, is_private=0)
	dir_path_idx = file_path.rfind('/')
	dir_path =file_path[0:dir_path_idx] + '/'

	#Append all attachments to final pdf
	for pdfs in attached_docs:
		if _('Merged_').format(docid) in pdfs.file_name:
			return dir_path + final_merged_file
		else: 
			to_merge =PyPDF2.PdfFileReader(dir_path+pdfs.file_name)
			mergeFile.append(to_merge,'rb')

	#create merged pdf file and add it as attachment to docid
	if mergeFile:
		mergeFile.write(dir_path +final_merged_file)
		mergeFile.close()
		file_stats = os.stat(dir_path + final_merged_file)
		file_size = file_stats.st_size
		
		merged_file = frappe.get_doc({
					"doctype": "File",
					"file_name":final_merged_file,
					"file_url": "/files/" + final_merged_file,
					"attached_to_doctype": doctype,
					"attached_to_name": docid,
					"file_size":file_size,
					"is_private":0
				})
		merged_file.insert()
	
	return dir_path + final_merged_file