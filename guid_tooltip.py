import sublime, sublime_plugin  

import os
import fnmatch
from os.path import join

class GUIDTooltip(sublime_plugin.EventListener):  
	files_by_guid = {}
	filenames_by_guid = {}
	relative_path_by_guid = {}
	def get_all_guid_files(self, view):
		window_variables = view.window().extract_variables()

		project_path = ''

		if 'project_path' in window_variables:
			project_path = window_variables["project_path"]
		else:
			file_name = view.file_name()
			for i in range(0,len(file_name)):
				if file_name[i] == 'A' and file_name[i+1] == 's' and file_name[i+2] == 's' and file_name[i+3] == 'e' and file_name[i+4] == 't' and file_name[i+5] == 's':
					potential_project_path = file_name[:i]
					if os.path.isdir(join(potential_project_path, "Assets")) and os.path.isdir(join(potential_project_path, "ProjectSettings")):
						project_path = potential_project_path
					else:
						return False
		

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
				self.relative_path_by_guid[guid] = join(root, filename)[len(project_path):-5]

		return True

	def on_selection_modified_async(self, view):
		if not self.get_all_guid_files(view):
			return

		for region in view.sel():
			selected_text = view.substr(region)

			def open_file(file):
				view.window().open_file(file)

			if selected_text in self.files_by_guid:
				
				view.set_status('guid_info', self.files_by_guid[selected_text])
				view.show_popup('<b>' + self.relative_path_by_guid[selected_text] + '</b><br><a href="' + self.files_by_guid[selected_text] + '">Open</a>', on_navigate=open_file)


