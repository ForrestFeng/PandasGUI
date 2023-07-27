# July 25, 2023 
## How to install pip install from a local package

This is useful to do local test to ensure that the package works well
A: just run 
   pip install /path/to/local/package


## How do I drop NA within pandas.DataFrame.query
A: df.query("A == A")

## How to query col with string and empty data with col.str.contains('abc')
A: First need to drop NA in col then query it
	df.query("A == A & A.str.contains('xyz')")


## Any tips to use pandas.query(exp)
A: index can be used directly
	df.query('index < b < c') 
	df.query('index > 2')

A:  And logic
   df.query('(a < b) & (b < c)')
   df.query('a < b and b < c')
   
A: Col equal, great, ...
	df.query('color == "red"')
	
	
	df.query('expr = '0.0 <= a <= c <= 0.5')
	
A: in 
	df.query('a in b')
	df.query('a not in b')
	df.query('a in b and c < d')
	
	
A: list with ==, !=
	df.query('col == ["a", "b", "c"]') # col of 'a', 'b' or 'c' will be selected
	same as 
	df.query('["a", "b", "c"] in col')
	
	
	df.query('c != [1, 2]') # same to 
	df.query('[1, 2] not in c')
	
A: not and ~ to negate boolean expressions with the word not or the ~ operator.
	df.query('~bools')
	df.query('not bools')
	df.query('a < b < c and (not bools) or bools > 2')
	
	
## How to use query with date?
A: df.query(( 'Date < '2007-02-03'")


## How to allow user to add new columns in pandasgui


A2: eval  with multi-line assignment, NewCx will be added in the result df

Use df.eval(""" 
				NewC1 = A + B
				NewC2 = A * 2
				NewC3 = A + B
				NewC4 = C.str.extract("regex_with_ONLY_ONE_group")
				""",
				inplace = False
				)
				
				
See https://www.askpython.com/python-modules/pandas/pandas-eval#:~:text=Pandas%20eval%20%28%29%3A%20Evaluate%20a%20Python%20expression%20as,on%20using%20the%20Pandas%20eval%20%28%29%20method.%20


A2: use str.extract with multi-groups to select into a new DataFrame with mult-columns named 1 and 2
df.eval('StrColumn.str.extract("(Ivy)(saur)"), expand=True')

NOTE: if a column contains space or need enclose it with ``



## Any EvalScript Samples
A. create new col with existing one(allow multi lines )
	M = B + C	
	
	N = B + 3.4
	
	P = B ** 2
	
A2. find uniqe values of col 
	A.unique()
	
A3. extract words from one column with regex
	B.str.extract( '(pattern1)' )
	B.str.extract( '(pattern1)(pattern2)(pattern3)' )
	
A4. extract number from column
	B.str.extract( '(\d+)' )
	
	
	
	