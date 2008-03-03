#
# This query delete old lsc commands (now - 1 month)
#

DELETE
	commands,
	commands_on_host,
	commands_history
FROM
	commands A,
	commands_on_host B,
	commands_history C
WHERE
	A.date_created < (DATE_SUB(NOW(), INTERVAL 1 MONTH)) AND
	A.id_command = B.id_command AND
	B.id_command_on_host = C.id_command_on_host
	
