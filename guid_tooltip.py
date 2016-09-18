import sublime, sublime_plugin  

import os
import fnmatch
from os.path import join

class GUIDTooltip(sublime_plugin.EventListener):  
	files_by_guid = {}
	filenames_by_guid = {}
	relative_path_by_guid = {}
	gameobject_name_by_id = {}
	row_by_id = {}
	def parse_yaml(self, view):
		filename = view.file_name()
		l = len(filename)

		if filename.lower().endswith(('.unity','.prefab')):
			with open(filename) as f:
					content = f.readlines()
			total_lines = len(content)

			current_go_id = ''
			found_go = False
			current_go_line = 0

			for i in range(1, total_lines):
				line = content[i]
				last_line = content[i-1]

				if last_line.find('--- !u!') != -1 and line.find("GameObject") != -1:
					current_go_id = last_line[10:-1]
					current_go_line = i
					found_go = True

				if found_go and line.find("m_Name") != -1:
					self.gameobject_name_by_id[current_go_id] = line[9:-1]
					self.row_by_id[current_go_id] = current_go_line
					found_go = False
					current_go_id = ''


	def get_all_guid_files(self, view):
		window_variables = view.window().extract_variables()

		project_path = ''

		if 'project_path' in window_variables:
			project_path = window_variables["project_path"]
		else:
			file_name = view.file_name()

			if file_name == None:
				return False

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

		self.parse_yaml(view)

		for region in view.sel():
			selected_text = view.substr(region)

			def open_file(file):
				view.window().open_file(file)

			def go_to_gameobject(id):
				if view.window().active_view():
					row = self.row_by_id[id]
					col = 1
					print("Trying to go to line " + str(row))
					view.window().active_view().run_command(
							"goto_row_col",
							{"row": row, "col": col}
					)

			if selected_text in self.files_by_guid:
				view.set_status('guid_info', self.files_by_guid[selected_text])
				view.show_popup('<b>' + self.relative_path_by_guid[selected_text] + '</b><br><a href="' + self.files_by_guid[selected_text] + '">Open</a>', on_navigate=open_file)

			if selected_text in self.gameobject_name_by_id:
				view.set_status('guid_info', self.gameobject_name_by_id[selected_text])
				view.show_popup('<b>GameObject: ' + self.gameobject_name_by_id[selected_text] + 
					'</b><br><a href="' + selected_text + '">Show</a>', on_navigate=go_to_gameobject)

