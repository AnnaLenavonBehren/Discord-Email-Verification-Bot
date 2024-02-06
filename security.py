def valid_email(email:str):
	ending = email.endswith("") 	# gmx.de, gmail.com or the ending of your university's email address
	blacklist = [" ", ";"] 			# to prevent SQL injection
	for b in blacklist:
		if b in email:
			return False
	return ending