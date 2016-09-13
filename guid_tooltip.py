import sublime, sublime_plugin  

import os
import fnmatch
from os.path import join

class GUIDTooltip(sublime_plugin.EventListener):  
	files_by_guid = {}
	filenames_by_guid = {}
	def get_all_guid_files(self, view):
		project_path = view.window().extract_variables()['project_path']

		for root, subFolders, files in os.walk(project_path):
			for filename in fnmatch.filter(files, '*.meta'):
				with open(join(root, filename)) as f:
					content = f.readlines()

				guid = ''
				for line in content:
					if line.find('guid:') != -1:
						guid = line[6:(len(line)-1)]
				# print(filename + ": " + guid)
				self.files_by_guid[guid] = join(root, filename)[:-5]
				self.filenames_by_guid[guid] = filename[:-5]

	def on_selection_modified_async(self, view):
		self.get_all_guid_files(view)

		for region in view.sel():
			selected_text = view.substr(region)

			def open_file(file):
				view.window().open_file(file)

			if selected_text in self.files_by_guid:
				
				view.set_status('guid_info', self.files_by_guid[selected_text])
				view.show_popup('<b>' + self.filenames_by_guid[selected_text] + '</b><br><a href="' + self.files_by_guid[selected_text] + '">Click Me</a>', on_navigate=open_file)


