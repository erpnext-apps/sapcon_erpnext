
from heapq import merge
import frappe
import os
import json
import io
from frappe import _

import PyPDF2

@frappe.whitelist()
def custom_pdf_merge(doctype,docid,attach_to_og_doc=False,doc_to_merge={}):

	"""
		doc_to_merge = {
			"dt_to_merge": "", ##doctype on which merge is to be performed
			"dt_to_merge_id": "",  ##docid on which merge is to be performed
			"attach_fieldname": "", ##fieldname of the attach field through which CAD doc is uploaded (Ex:assembly_drawing)
			"print_format": "", ##preferred print format of docid
			"attach_to_doc": True/False, ##should the merged pdf be attached to dt_to_merge_id
			"other_attachments_to_merge":  [list of file names] ##list of pdfs attached to dt_to_merge_id that need to be merged along with attach_fieldname
		}

	"""

	doc_to_merge=json.loads(doc_to_merge)

	file_path = frappe.utils.get_url()
	dir_path_idx = file_path.find('/')+2
	#dir_path =file_path[dir_path_idx:]
	dir_path = frappe.get_site_path()

	mergeFile = PyPDF2.PdfFileMerger()

	final_merged_file = _("/private/files/Merged_{}.pdf").format(doc_to_merge['dt_to_merge_id'])

	# Generate pdf of original record
	org_pdf = doc_to_merge['dt_to_merge_id'] + ".pdf"
	doc_pdf = frappe.attach_print(doc_to_merge['dt_to_merge'], doc_to_merge['dt_to_merge_id'],
				str(doc_to_merge['dt_to_merge_id']), print_format=doc_to_merge['print_format'])

	with open(org_pdf, "w") as docfile:
		docfile.write(doc_pdf["fcontent"])

	# Append pdf of original record
	og_doc_to_merge = PyPDF2.PdfFileReader(org_pdf,'r')
	mergeFile.append(og_doc_to_merge,'r')

	attachment_filename = frappe.get_value(doc_to_merge['dt_to_merge'],
						doc_to_merge['dt_to_merge_id'],
						doc_to_merge['attach_fieldname'])

	idx = attachment_filename.rfind('/')+1
	attachment_filename = attachment_filename[idx:]

	# Fetch attachment details
	attached_doc = frappe.get_all("File",
			fields=["name", "file_name", "file_url"] ,
			filters = {
				"attached_to_name": doc_to_merge['dt_to_merge_id'],
				"attached_to_doctype": doc_to_merge['dt_to_merge'],
				"file_name":attachment_filename})
	
	if 'other_attachments_to_merge' in doc_to_merge:
		other_attachments_str = ",".join(doc_to_merge['other_attachments_to_merge'])
	else:
		other_attachments_str = ''
		
	other_attached_docs = frappe.get_all("File",
				fields=['name','file_name','file_url'],
				filters={
					"attached_to_name": doc_to_merge['dt_to_merge_id'],
					"attached_to_doctype": doc_to_merge['dt_to_merge'],
					"file_name":['in',other_attachments_str]
				})

	old_merged_doc = frappe.get_all("File",
				fields=['name','file_name','file_url'],
				filters={
					"attached_to_name": ['in',(docid,doc_to_merge['dt_to_merge_id'])],
					"attached_to_doctype": ['in',(doctype,doc_to_merge['dt_to_merge'])],
					"file_name":['like','Merged_'+doc_to_merge['dt_to_merge_id']+'.pdf']
				})


	# Delete old Merged file
	for doc in old_merged_doc:
		frappe.delete_doc("File",doc.name)

	# Append main attachment to merge file
	if attached_doc and len(attached_doc) > 0:
		url = attached_doc[0].file_url
		if not attached_doc[0].file_url.startswith('/private'):
			url = '/public' + attached_doc[0].file_url
		to_merge =PyPDF2.PdfFileReader(dir_path + url)
		mergeFile.append(to_merge,'r')

	# Append other attachments to final pdf
	for pdfs in other_attached_docs:
		url = pdfs.file_url
		if not pdfs.file_url.startswith('/private'):
			url = '/public' + pdfs.file_url
		to_merge =PyPDF2.PdfFileReader(dir_path + url)
		mergeFile.append(to_merge,'r')

	if mergeFile:
		mergeFile.write(dir_path + final_merged_file)
		mergeFile.close()

		file_stats = os.stat(dir_path + final_merged_file)
		file_size = file_stats.st_size

		if attach_to_og_doc == 1:
			merged_file = frappe.get_doc({
                                "doctype": "File",
                                "file_name": "Merged_"+doc_to_merge['dt_to_merge_id']+".pdf",
                                "file_url": final_merged_file,
                                "attached_to_doctype": doctype,
                                "attached_to_name": docid,
                                "file_size":file_size,
				"is_private": 1
                        })
			merged_file.insert()

		merged_file = frappe.get_doc({
				"doctype": "File",
				"file_name": "Merged_"+doc_to_merge['dt_to_merge_id']+".pdf",
				"file_url":final_merged_file,
				"attached_to_doctype": 'BOM',
				"attached_to_name": doc_to_merge['dt_to_merge_id'],
				"file_size":file_size,
				"is_private": 1
			})
		merged_file.insert()



	return {'file_url' : merged_file.file_url,
		'attached_to' : merged_file.attached_to_name}



@frappe.whitelist()
def download_merged_pdf(file_url,attached_to):

	_byteIo = io.BytesIO()

	pdfFile = open(frappe.get_site_path() + file_url.strip(), 'r')
	pdfReader = PyPDF2.PdfFileReader(pdfFile)
	pdfWriter = PyPDF2.PdfFileWriter()
	for pageNum in range(pdfReader.numPages):
		pageObj = pdfReader.getPage(pageNum)
		pdfWriter.addPage(pageObj)
	pdfWriter.write(_byteIo)

# Download merged file
	frappe.local.response.filename = "Merged_"+attached_to+".pdf"
	frappe.local.response.filecontent = _byteIo.getvalue()
	frappe.local.response.type = 'download'
