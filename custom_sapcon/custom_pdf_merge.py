
from heapq import merge
import frappe
import os
from frappe import _

import PyPDF2

@frappe.whitelist()
def custom_pdf_merge(doctype,docid):

	mergeFile = PyPDF2.PdfFileMerger()

	final_merged_file = _("/private/files/Merged_{}.pdf").format(docid)

	#Generate pdf of original record
	org_pdf = docid + ".pdf"
	doc_pdf = frappe.attach_print(doctype, docid,str(docid), print_format="")
#	docfile = open(_("{}.pdf").format(docid),'w+')
	docfile = open(org_pdf,"wb")
	docfile.write(doc_pdf["fcontent"])
	doc_to_merge = PyPDF2.PdfFileReader(org_pdf,'rb')
	mergeFile.append(doc_to_merge,'rb')

	#Fetch attachments
	attached_docs = frappe.get_all("File",
			fields=["name", "file_name", "file_url"] ,
			filters = {"attached_to_name": docid, "attached_to_doctype": doctype,"file_name":["like","%.pdf"]})

	file_path = frappe.utils.get_url()

	dir_path_idx = file_path.find('/')+2
	dir_path =file_path[dir_path_idx:]

#	print (dir_path)

	#Append all attachments to final pdf
	for pdfs in attached_docs:
		if _('Merged_').format(docid) in pdfs.file_name:
			return dir_path + final_merged_file
		else:
#			print (dir_path + pdfs.file_url)
			to_merge =PyPDF2.PdfFileReader(dir_path + pdfs.file_url)
			mergeFile.append(to_merge,'rb')

	#create merged pdf file and add it as attachment to docid
	if mergeFile:
#		print (dir_path + final_merged_file)
		mergeFile.write(dir_path + final_merged_file)
		mergeFile.close()
		file_stats = os.stat(dir_path + final_merged_file)
		file_size = file_stats.st_size

		merged_file = frappe.get_doc({
					"doctype": "File",
					"file_name": "Merged_"+docid+".pdf",
					"file_url":final_merged_file,
					"attached_to_doctype": doctype,
					"attached_to_name": docid,
					"file_size":file_size,
				})
		merged_file.insert()
#	frappe.msgprint(dir_path + final_merged_file)
	return dir_path + final_merged_file