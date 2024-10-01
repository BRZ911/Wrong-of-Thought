
POT_ANSWER_SYSTEM = """
You are an expert in writing Python code to solve mathematical problems. You need to rewrite Python code to solve mathematical problems and determine whether the answer is correct or incorrect. I will give you a few examples.
"""
POT_ANSWER = """
Error examples:
1. Question: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?
# Python code:
money_initial = 23
bagels = 5
bagel_cost = 2 
money_spent = bagels * bagel_cost
money_left = money_initial + money_spent 
ans = money_left
The final answer is: ans = 33

Judgment process:
Let's start by rewriting the Python code correctly for the problem described, and then we'll evaluate the previous result.
Here is the corrected version of the code:
money_initial = 23
bagels = 5
bagel_cost = 3
money_spent = bagels * bagel_cost
money_left = money_initial - money_spent
ans = money_left
This code will correctly calculate how much money Olivia has left after buying the bagels. Let's run this corrected code to confirm the right answer.
The corrected Python code calculates that Olivia has $8 left after buying the bagels.
Comparing this to the original code:
The bagel cost was mistakenly set to $2 instead of $3.
The operation for calculating the remaining money was incorrectly using addition instead of subtraction.
Therefore, the original result of $33 was incorrect. The correct amount of money Olivia has left is $8

Decision: Error


2. Question: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?
# Python code:
golf_balls_initial = 58
golf_balls_lost_tuesday = 23
golf_balls_lost_wednesday = 2
golf_balls_left = golf_balls_initial + golf_balls_lost_tuesday + golf_balls_lost_wednesday
ans = golf_balls_left
The final answer is: ans = 83

Judgment process:
To solve the problem correctly, we need to ensure that the number of golf balls Michael lost is subtracted from his initial amount, rather than added.
golf_balls_initial = 58
golf_balls_lost_tuesday = 23
golf_balls_lost_wednesday = 2
golf_balls_left = golf_balls_initial - golf_balls_lost_tuesday - golf_balls_lost_wednesday
ans = golf_balls_left
The corrected Python code calculates that Michael has 33 golf balls left at the end of Wednesday.
Comparing this to the original code:
The original code incorrectly added the number of lost golf balls to the initial amount, resulting in an incorrect final answer of 83 golf balls.
The correct operation should have subtracted the lost golf balls from the initial count.
Therefore, the original result of 83 was incorrect. The correct number of golf balls Michael has left is 33.

Decision: Error


3. Question: There were nine computers in the server room. Five more computers were installed each day, from monday to thursday. How many computers are now in the server room?
# Python code:
computers_initial = 9
computers_per_day = 5
num_days = 3
computers_added = computers_per_day * num_days
computers_total = computers_initial - computers_added
ans = computers_total
The final answer is: ans = -6

Judgment process:
To solve the problem correctly, it's crucial to ensure that the number of computers added over the days is added to the initial count. Also, it appears that the calculation of the number of days is incorrect.
computers_initial = 9
computers_per_day = 5
num_days = 4 
computers_added = computers_per_day * num_days
computers_total = computers_initial + computers_added
ans = computers_total
The corrected Python code calculates that there are now 29 computers in the server room.
Comparing this to the original code:
The original code incorrectly set the number of days as 3 instead of 4.
Additionally, it incorrectly subtracted the number of added computers from the initial count, leading to a mistaken negative result of -6.
Therefore, the original result of -6 was incorrect. The correct number of computers in the server room, after adding the new installations from Monday to Thursday, is 29.

Decision: Error


4. Question: Shawn has five toys. For Christmas, he got two toys each from his mom and dad. How many toys does he have now?
# Python code:
toys_initial = 5
mom_toys = 2
dad_toys = 2
total_received = mom_toys * dad_toys
total_toys = toys_initial * total_received
ans = total_toys
The final answer is: ans = 20

Judgment process:
To solve this problem correctly, we need to ensure that the number of toys Shawn received from his mom and dad are added together, and then this sum is added to his initial toy count. The operations in the provided code incorrectly use multiplication.
Here is the corrected Python code:
toys_initial = 5
mom_toys = 2
dad_toys = 2
total_received = mom_toys + dad_toys
total_toys = toys_initial + total_received
ans = total_toys
Comparing this to the original code:
The original code incorrectly used multiplication both for combining the toys from mom and dad and for adding them to the initial count, which resulted in a final answer of 20.
The correct method is to sum the toys received from each parent and then add that sum to the initial number of toys.
Therefore, the original result of 20 was incorrect. The correct total number of toys Shawn has after receiving gifts from his parents is 9.

Decision: Error



Right examples:
1. Question: Jason had 20 lollipops. He gave Denny some lollipops. Now Jason has 12 lollipops. How many lollipops did Jason give to Denny?
# Python code:
jason_lollipops_initial = 20
jason_lollipops_after = 12
denny_lollipops = jason_lollipops_initial - jason_lollipops_after
ans = denny_lollipops
The final answer is: ans = 8

Judgment process:
To address the question from scratch using Python code.
Here's how the Python code should look to solve this:
jason_lollipops_initial = 20
jason_lollipops_after = 12
denny_lollipops = jason_lollipops_initial - jason_lollipops_after
ans = denny_lollipops
This code will calculate the correct number of lollipops Jason gave to Denny. Let's run this code to confirm the solution is correct.
Therefore, the Python code calculates that Jason gave Denny 8 lollipops. This confirms that the initial code provided with the question is correct. The final answer of 8 lollipops is indeed accurate based on the scenario described.

Decision: Right


2. Question: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in total?
# Python code:
leah_chocolates = 32
sister_chocolates = 42
total_chocolates = leah_chocolates + sister_chocolates
chocolates_eaten = 35
chocolates_left = total_chocolates - chocolates_eaten
ans = chocolates_left
The final answer is: ans = 39

Judgment process:
To solve this problem accurately, let's review and confirm each step of the provided Python code.
Here's the provided code:
leah_chocolates = 32
sister_chocolates = 42
total_chocolates = leah_chocolates + sister_chocolates
chocolates_eaten = 35
chocolates_left = total_chocolates - chocolates_eaten
ans = chocolates_left
This code should accurately calculate the remaining chocolates by first determining the total number of chocolates they started with and then subtracting the number they ate. Let's verify the calculation to ensure the final answer of 39 is correct.
Therefore, the Python code correctly calculates that Leah and her sister have 39 chocolates left in total after eating 35. The process followed in the code matches the problem's requirements, and the final answer of 39 is accurate. 

Decision: Right


3. Question: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars are in the parking lot?
# Python code:
cars_initial = 3
cars_arrived = 2
total_cars = cars_initial + cars_arrived
ans = total_cars
The final answer is: ans = 5

Judgment process:
Let's solve the problem from scratch using Python code.
The correct Python code to solve this would look like this:
cars_initial = 3
cars_arrived = 2
total_cars = cars_initial + cars_arrived
ans = total_cars
This code calculates the total number of cars by adding the number that were initially there to the number that arrived. Let's execute this code to confirm the solution.
Therefore, the Python code, when rewritten from scratch, confirms that there are now 5 cars in the parking lot after 2 more cars arrived. The approach and calculation are correct, and the final answer of 5 is accurate based on the scenario described.

Decision: Right


4. Question: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are done, there will be 21 trees. How many trees did the grove workers plant today?
# Python code:
trees_initial = 15
trees_after = 21
trees_added = trees_after - trees_initial
ans = trees_added
The final answer is: ans = 6

Judgment process:
To address the question effectively using Python, let's start by writing the code from scratch based on the provided problem.
Here is how the Python code should be structured:
trees_initial = 15
trees_after = 21
trees_added = trees_after - trees_initial
ans = trees_added
This code is intended to calculate how many trees were added by subtracting the initial number from the total after the planting. Let's execute this code to confirm that the correct number of trees planted is indeed 6.
Therefore, the Python code correctly calculates that 6 trees were planted today. The calculation approach is accurate for the given scenario, where the number of trees after planting is subtracted from the initial number to determine how many were added. The final answer of 6 is indeed correct.

Decision: Right



Question: {question}
# Python code: \n {reason_pot}
The final answer is: ans = {reason_pot_ans}

Please judge step by step  whether this answer is correct.
Finally, you need to provide an answer format: 'Decision: Right/Error'
""".strip() + "\n"