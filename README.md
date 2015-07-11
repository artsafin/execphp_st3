### ExecPhp plugin for Sublime Text 3

This small tool allows to execute selection or the whole file as PHP code in Sublime Text 3.
The code is executed with local interpreter that must to be preinstalled.

##### Why
The internal build functionality requires first saving to file, while sometimes it is more convenient to quickly test something in scratch files and close without saving.

By default PHP interpreter is ran with the following command:
```
php -ddisable_functions= -ddisplay_errors=On -derror_reporting=-1 -f <FILENAME>
```
where `<FILENAME>` is a temporary file generated by the plugin with selection from the buffer.

#### Configuration

There are `Execute as PHP: Default settings` and `Execute as PHP: User settings` actions in Command Palette leading to corresponding configuration files.

Option  | Description
--------|------------
timeout | Sets the timeout of waiting of PHP process to finish. Process is killed once time is out.
phpCmd  | Command to run the PHP interpreter

#### Key binding

By default the command is not binded to any key and is only runnable as `Execute as PHP` from Command Palette.
The command name for manual key binding is `exec_php`.

