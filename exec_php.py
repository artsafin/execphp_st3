import sublime, sublime_plugin
import tempfile, subprocess, os

class ExecPhpCommand(sublime_plugin.TextCommand):
	timeout = None
	phpCmd = None
	resultWnd = None

	def get_php_cmdline(self, filename):
		return list(map(lambda x: x.replace("$file", filename), self.phpCmd))

	def load_settings(self):
		default_pref = sublime.load_settings("ExecPhp.sublime-settings")
		user_pref = sublime.load_settings("Preferences.sublime-settings")

		self.timeout = user_pref.get("timeout") if user_pref.has('timeout') else default_pref.get("timeout")
		self.phpCmd = user_pref.get("phpCmd") if user_pref.has('phpCmd') else default_pref.get("phpCmd")
		self.resultWnd = user_pref.get("resultWnd") if user_pref.has('resultWnd') else default_pref.get("resultWnd")

	def run(self, edit):
		self.load_settings()
		self.output_init(self.view.window())

		text = self.get_text_from_view(self.view)
		text = self.prepend_php_tag_if_needed(text)
		# sublime.message_dialog("selection: "+text)

		filename = self.write_to_tempfile(text)
		if filename == None:
			return

		cmdline = self.get_php_cmdline(filename)
		self.output_writeln("[Running command: %s]" % str(cmdline))
		try:
			out, err, returncode = self.cmd_exec_wait(cmdline)
			self.output_writeln("[Exit code %d]" % returncode)
			if len(err) > 0:
				self.output_writeln("[Stderr]:\n%s" % err)

			self.output_writeln(out)
		except subprocess.TimeoutExpired:
			self.output_writeln("[Timeout of %ds exceeded, process killed]" % self.timeout)
		finally:
			os.remove(filename)

	def write_to_tempfile(self, text):
		filename = None
		with tempfile.NamedTemporaryFile(delete=False) as fp:
			filename = fp.name
			fp.write(bytes(text, 'UTF-8'))
		return filename

	def cmd_exec_wait(self, cmdline):
		si = None
		if sublime.platform() == "windows":
			si = subprocess.STARTUPINFO()
			si.dwFlags = subprocess.STARTF_USESHOWWINDOW
			si.wShowWindow = subprocess.SW_HIDE

		with subprocess.Popen(cmdline,
							  universal_newlines = True,
							  stdout = subprocess.PIPE,
							  stderr = subprocess.PIPE,
							  startupinfo = si) as proc:
			try:
				out, err = proc.communicate(timeout=self.timeout)
				return (out, err, proc.returncode)
				
				# result = "Stdout: %s\n\nStderr: %s" % (out, err)
				# sublime.message_dialog(result)
				# self.output_writeln(result)
			except subprocess.TimeoutExpired:
				proc.kill()
				raise

	def output_init(self, window):
		if not hasattr(self, 'output'):
			self.output = window.create_output_panel("exec_php")
			for (k, v) in self.resultWnd.items():
				self.output.settings().set(k, v)
			self.output.assign_syntax("Packages/Text/Plain text.tmLanguage")
		window.run_command('show_panel', {'panel': 'output.exec_php'})

	def output_writeln(self, str):
		if not hasattr(self, 'output'):
			sublime.status_message("call to writeln before output init")
		else:
			self.output.run_command('append', {'characters': str + "\n", 'force': True, 'scroll_to_end': True})

	def report_file_status(self, filename, str = None):
		if (filename == None):
			sublime.status_message("no tmp file")
		else:
			if (str == None):
				sublime.status_message("file: %s" % (filename))
			else:
				sublime.status_message("file: %s: %s" % (filename, str))

	def get_text_from_view(self, view):
		sel = view.sel()
		
		region = self.squash_regions(sel)
		
		if not region.empty():
			return view.substr(region)
		else:
			return view.substr(sublime.Region(0, view.size()))

	def prepend_php_tag_if_needed(self, text):
		if text.lstrip().startswith("<?"):
			return text
		else:
			return "<?php\n" + text

	def squash_regions(self, selection):
		a = 0
		b = 0
		for region in selection:
			if a == b:
				a = region.a
				b = region.b
				continue
			a = min(a, region.a)
			b = max(b, region.b)
		
		return sublime.Region(a, b)