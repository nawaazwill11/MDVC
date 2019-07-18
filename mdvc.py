import re, json, os

class Formula(object):
	'''Formula operations'''

	def doFormulas(self):
		'''Calls the function by option choice.'''
		self.forOps[self.operator]()

	def flen(self):
		'''Returns the lenght of current formulas.'''
		return len(self.formulas.keys())

	def formulaNameList(self):
		'''Returns a list of all the names in a formula.'''
		return re.findall('[a-zA-Z_][a-zA-Z0-9_]+', self.formula)

	def varNameList(self):
		'''Returns a list of all variables names.'''
		return self.variables.keys()

	def namesExists(self):
		''''Checks if names in the formula are present in the variable name list.'''
		for i in self.formulaNameList():
			if i not in self.varNameList():
				return False, i
		return True, ''

	def formedFormula(self, formula):
		'''Creates a valid formula'''
		pos = 0
		for f in self.formulaNameList():
			formula = formula[:formula.find(f, pos)] + 'float(self.variables[\'' + f + '\'])' + formula[formula.find(f, pos) + len(f):]
			pos = formula.find(f, pos) + 1
		return formula.strip()

	def executeFormula(self, formula):
		'''Executes the well-formed formula.'''
		try:
			exec('self.result=' + formula)
			self.result = self.integral(self.result)
			return True
		except Exception as e:
			print('Execution failed.')

	def integral(self, update):
		'''Removes trailing zeros from a number.'''
		if re.match('^[0-9]+.[0]+$', str(update)):
			return int(update)
		return float(update)
	
	def testFormula(self):
		'''Test runs a given formula.'''
		self.applyFormula(self.formula)
		print(self.result)

	def applyFormula(self, formula):
		'''Executes the formula return from formedFormula() function.'''
		if self.namesExists()[0]:
			try:
				self.executeFormula(self.formedFormula(formula))
				return True
			except Exception as e:
				print('Bad formula.', e)
		else:
			print('name {} not found'.format(self.namesExists()[1]))
			return False

	def extractVF(self):
		'''Extracts the variable name and formula from the given command.'''
		vmatch = re.search('>\s[a-zA-Z_][a-zA-Z0-9_]+', self.command)
		if not vmatch:
			print('Bad variable name.')
			return '' 
		varname = self.command[vmatch.span()[0] + 2:vmatch.span()[1]]
		fmatch = re.search(varname + '\s[a-zA-Z0-9_]+', self.command)
		if not fmatch:
			print('Bad formula.')
			return ''
		formula = self.command[fmatch.span()[0] + len(varname) + 1:]
		return varname, formula
		

	def assignFtoV(self):
		'''Creates a new variable from results of arithmetic calculations.'''
		vf = self.extractVF()
		self.varname = vf[0]
		self.formula = vf[1]
		if not self.applyFormula():
			return ''
		self.addVariable(str(self.result)) #as result is in either float or int type.

	def addFormula(self):
		'''Adds a formula to the dynamic entry.'''
		if self.executeFormula(self.formedFormula(self.formula)):
			name = input('Name formula: ')
			self.formulas[name] = self.formula
			print('+ Formula Added')
		else:
			print('Formula failed to store.')

	def showFormulas(self):
		'''Shows all addedd formulas.'''
		if self.flen() == 0:
			print('No formulas available.')
			return ''
		else:
			param = self.command[4:]
			if len(param) > 1:
				if param in self.formulas.keys():
					print('{}: {}'.format(param, self.formulas[param]))
				else:
					print('No such formula.')

			for k, v in self.formulas.items():
				print('{}: {}'.format(k, v))

	def storeFormulas(self):
		'''Saves all formulas to a file.'''
		if 'formulas.json' in os.listdir():
			confirm = input('Stored formulas already exist. Override?(Y/N): ').lower()
			if confirm == 'n':
				print('Cancelled!')
				return ''
		file = open('formulas.json', 'w')
		json.dump(self.formulas, file, indent=4)
		print('Formulas stored!')

	def loadFormulas(self):
		'''Loads formulas from a file.'''
		if 'formulas.json' in os.listdir():
			if self.flen() > 0:
				if input('Current formulas will be overridden. Continue?(Y/N): ').lower() == 'n':
					return ''
			file = open('formulas.json', 'r')
			self.formulas = json.load(file)
			print('Formales loaded!')
		else:
			print('Nothing to load.')

	def removeFormula(self):
		'''Removes a specific formula passed to it.'''
		if self.formula not in self.formulas.keys():
			print('Not found:', self.formula)
			print('Available variables:\n', self.showFormulas())
		else:
			print('- variable deleted')
			del self.formulas[self.formula]

	def clearFormulas(self):
		'''Removes all the formulas from the dymamic entry.'''
		if self.flen() == 0:
			print('Nothing to clear.')
			return ''
		self.formulas = {}
		print('Cleared all formulas!')


class Variable(object):
	'''Variable operations'''

	def doVariables(self):
		'''Calls the function by option choice.'''
		self.varOps[self.operator]()

	def vlen(self):
		return len(self.variables.keys())

	def addVariable(self, *args):
		if self.varname in self.variables.keys():
			if input('{} already added. Override? (Y/N)').lower() == 'n':
				return ''
		print('{}: '.format(self.varname), end='')
		if len(args) != 0:
			value = args[0]
		else:
			value = input('')
		if not re.match('[0-9.]+', value):
			print('Bad value.')
			return ''
		self.variables[self.varname] = value
		print('+ variable added')

	def removeVariable(self):
		if self.varname not in self.variables.keys():
			print('Not found:', self.varname)
			print('Available variables:\n', self.showVariables())
		else:
			print('- variable deleted')
			del self.variables[self.varname]

	def hasParam(self):
		param = re.search('s(\s[a-zA-Z_][a-zA-Z0-9_]+)?$', self.command)
		if param:
			return self.command[param.span()[0] + 2:]
		

	def showVariables(self):
		if self.vlen() > 0:
			param = self.hasParam()
			if param:
				if param in self.variables.keys():
					print('{}: {}'.format(param, self.variables[param]))
				else:
					print('No variable', param)
			else:
				for var, val in self.variables.items():
					print('{}: {}'.format(var, val))
		else:
			print('No variables.')

	def storeVariables(self):
		if 'variables.json' in os.listdir():
			if self.vlen() == 0:
				print('Nothing to store.')
				return ''
			if input('Variable are already stored. Override? (Y/N)\n-> ').lower() == 'n':
				print('Cancelled')
				return ''
		file = open('variables.json', 'w')
		json.dump(self.variables, file, indent=4)
		print('Variables stored!')

	def loadVariables(self):
		if 'variables.json' not in os.listdir():
			print('Nothing to load!')
			return ''
		else:
			if self.vlen() > 0:
				if input('Warning: Already added variables will be overridden. Continue? (Y/N)').lower() == 'n':
					return ''
		file = open('variables.json', 'r')
		self.variables = json.load(file)
		print('Loaded!')

	def clearVariables(self):
		if self.vlen() == 0:
			print('Nothing to clear.')
		else:
			self.variables = {}
			print('Variables cleared!')
					
class Emulator(Variable, Formula):
	'''cost emulator'''

	def __init__(self):
		self.variables = {}
		self.formulas = {}
		self.varOps = {'+': self.addVariable, '-': self.removeVariable}
		self.forOps= {'+': self.addFormula, '-': self.removeFormula}
		self.result = 0
		self.start_emu()

	def getHelp(self):
		print('''
			---------------------------------------\n
			Mini Dynamic Variable Calculator (MDVC)
			---------------------------------------\n
			Description
			-----------
			MDVC allows you to add new variables and arithmetic formulas dynamically
			while performing calculations.
			You can add, remove and view variables and formulas as you work with the tool.
			It even lets you store and load variables and formulas onto you computer for later uses.
			Made in less than a day. :D

			Usage
			-----
			v - for working with variables.
			f - for working with formulas.

			Syntax
			------
			v|f option [argument(s)]

			Common options
			--------------
			s - shows all added entries.
			e.g. 
			> f s 
			(shows all dynamic entries of formulas similar for v.)

			+ - adds a new dynamic entry.
			- - removes an entry.
			clear - removes all dynamically the added entries from the workspace.
			store - stores all dynamically added entries to a .json file.
			load - loads the stored entries in to the workspace.

			f specific syntax
			------------------
			f t [formula] - test runs a user provided formula.
			f v > [new name] [value|formula] - create a formulated variable.
			e.g.
			> f v > rent 7000 + 500
			> f v > profit revenue - monthly_costs 

			----------
			Contribute
			----------
			Help me to improve the tool.

			-------
			Contact
			-------
			email: mastermindjim@gmail.com
			github: https://www.github.com/nawaazwill11
			'''
			)

	def getVariant(self):
		while True:
			command = input('> ').strip()
			if re.match('^exit$', command):
				print('Good-bye')
				import time
				time.sleep(1)
				os._exit(1)
			elif re.match('^help$', command):
				self.getHelp()
			elif re.match('^v', command):
				self.command = command
				if re.match('^v store$', command):
					self.storeVariables()
				elif re.match('^v load$', command):
					self.loadVariables()
				elif re.match('^v clear$', command):
					self.clearVariables()
				elif re.match('^v\ss(\s[a-zA-Z_][a-zA-Z0-9_]+)?$', self.command):
					self.showVariables()
				elif re.match('^v\s[+-]\s[a-zA-Z_]|[a-zA-Z_][a-zA-Z0-9_]+$', command):
					self.variant = command[0]
					self.operator = command[2]
					self.varname = command[4:].strip()
					self.doVariables()
				else:
					print('Invalid syntax')
			elif re.match('^f',command):
				self.command = command
				if re.match('^f', command):
					if re.match('^f\sv\s>\s[a-zA-Z_][a-zA-Z0-9_]+', command):
						self.assignFtoV()
					elif re.match('^f\ss$', self.command):
						self.showFormulas()
					elif re.match('^f\sload$', self.command):
						self.loadFormulas()
					elif re.match('^f\sstore$', self.command):
						self.storeFormulas()
					elif re.match('^f\st', self.command):
						self.testFormula()
					elif re.match('^f\sclear$', self.command):
						self.clearFormulas()
					elif re.match('^f\s[+-]\s[(a-zA-Z0-9.][\s.+\/*-a-zA-z()0-9]+', command):
						self.variant = command[0]
						self.operator = command[2]
						self.formula = command[4:].strip()
						self.doFormulas()
					else:
						print('Bad paramter')
			else:
				print('Invalid syntax')	

	def start_emu(self):
		print('Type help for usage information.\nType exit to end.')
		while True:
			variant = self.getVariant()


x = Emulator()