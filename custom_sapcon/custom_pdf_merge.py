
from heapq import merge
import frappe
import os
from frappe import _

import PyPDF2

@frappe.whitelist()
def custom_pdf_merge(doctype,docid,attach_to_doc=False,doc_to_merge={}):

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
	doc_to_merge={
		'dt_to_merge': "BOM",
		'dt_to_merge_id': 'BOM-AP - Sample-001',
		'attach_fieldname': 'assembly_drawing',
		'print_format': 'Test format',
		'attach_to_doc': True,
		'other_attachments_to_merge':['NF71146319605972FinanceInvoice.pdf','efg.pdf']
	}

	file_path = frappe.utils.get_url()
	dir_path_idx = file_path.find('/')+2
	dir_path =file_path[dir_path_idx:-5]	

	mergeFile = PyPDF2.PdfFileMerger()

	final_merged_file = _("/private/files/Merged_{}.pdf").format(doc_to_merge['dt_to_merge_id'])

	# Generate pdf of original record
	org_pdf = doc_to_merge['dt_to_merge_id'] + ".pdf"
	doc_pdf = frappe.attach_print(doc_to_merge['dt_to_merge'], doc_to_merge['dt_to_merge_id'],
				str(doc_to_merge['dt_to_merge_id']), print_format=doc_to_merge['print_format'])
#	docfile = open(_("{}.pdf").format(docid),'w+')
	docfile = open(org_pdf,"wb")
	docfile.write(doc_pdf["fcontent"])

	# Append pdf of original record 
	og_doc_to_merge = PyPDF2.PdfFileReader(org_pdf,'rb')
	mergeFile.append(og_doc_to_merge,'rb')

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

	other_attachments_str = ",".join(doc_to_merge['other_attachments_to_merge'])
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
					"attached_to_name": doc_to_merge['dt_to_merge_id'],
					"attached_to_doctype": doc_to_merge['dt_to_merge'],
					"file_name":['like','Merged%']
				})
	# Delete old Merged file
	if old_merged_doc:
		frappe.delete_doc("File",old_merged_doc[0].name)
		print ('deleted' + old_merged_doc[0].file_name)

	# Append main attachment to merge file
	if attached_doc:
		to_merge =PyPDF2.PdfFileReader(dir_path + attached_doc[0].file_url)
		mergeFile.append(to_merge,'rb')

	# Append other attachments to final pdf
	for pdfs in other_attached_docs:
#		to_merge =PyPDF2.PdfFileReader(pdfs.file_url)
		to_merge =PyPDF2.PdfFileReader(dir_path + pdfs.file_url)
		mergeFile.append(to_merge,'rb')

	if mergeFile:
		# print (dir_path + final_merged_file)
		mergeFile.write(dir_path+final_merged_file)
		mergeFile.close()

		# Download merged file
		frappe.response['filename'] = "Merged_"+doc_to_merge['dt_to_merge_id']+".pdf"
		frappe.response['filecontent'] = mergeFile
		frappe.response['type'] = 'download'

		file_stats = os.stat(dir_path+final_merged_file)
		file_size = file_stats.st_size

		if attach_to_doc:
			merged_file = frappe.get_doc({
						"doctype": "File",
						"file_name": "Merged_"+doc_to_merge['dt_to_merge_id']+".pdf",
						"file_url":final_merged_file,
						"attached_to_doctype": doctype,
						"attached_to_name": docid,
						"file_size":file_size,
					})
			merged_file.insert()
		merged_file = frappe.get_doc({
					"doctype": "File",
					"file_name": "Merged_"+doc_to_merge['dt_to_merge_id']+".pdf",
					"file_url":final_merged_file,
					"attached_to_doctype": 'BOM',
					"attached_to_name": doc_to_merge['dt_to_merge_id'],
					"file_size":file_size,
				})
		merged_file.insert()
	

#	frappe.msgprint(dir_path + final_merged_file)
	return final_merged_file
