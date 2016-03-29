def embolden(str):
	return ""+str+""
	#return str
	#return str.upper()
	#return "" + str.upper() + ""
	
def listtostr(list, conj="and"):
	return ", ".join(list[:-1]) + " " + conj + " " + list[-1] if len(list) > 1 else list[0]