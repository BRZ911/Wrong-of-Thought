
EOT_PROCESS_SYSTEM = """
You are a senior mathematics teacher. Below are some mathematical equations written by students to solve problems. Now it is up to you to determine whether these equations are correct. I will give you some reference examples. You need to provide a final answer format: 'Decision: Right/Error'
""".strip()
EOT_PROCESS = r"""
Error examples:
1. Question: Arnel had ten boxes of pencils with the same number of pencils in each box.  He kept ten pencils and shared the remaining pencils equally with his five friends. If his friends got eight pencils each, how many pencils are in each box?

Equation solving process:
% Assume there are x pencils in each box:
pencil_per_box = x
% Arnel had ten boxes of pencils with the same number of pencils in each box:
total_pencil = 10 * pencil_per_box
% He kept 10 pencils:
pencil_kept = 10
% He shared the remaining pencils equally with his 5 friends, his friends got eight pencils each:
pencil_gave = 8 * 5
% The total number of pencils is incorrectly stated as just the sum of kept and given away pencils, which is incorrect as it should consider the initial total:
total_pencil = pencil_kept + pencil_gave
% How many pencils are in each box? The answer is pencil_per_box:
ans = pencil_per_box

Judgment process:
The major flaw in this equation setup lies in the statement 'total_pencil = pencil_kept + pencil_gave'. This equation incorrectly suggests that the total number of pencils Arnel had initially equals the sum of the pencils he kept plus the pencils he gave away. However, this neglects the fact that the total number of pencils originally was from 10 full boxes. It inaccurately ties the total pencils to the outcome of the sharing process, rather than starting with the full count from all boxes and subtracting what was kept and given. Thus, the correct calculation of total pencils should independently calculate from the number of boxes and pencils per box, not from the division afterward.

Decision: Error



2. Question: Larry spends half an hour twice a day walking and playing with his dog. He also spends a fifth of an hour every day feeding his dog. How many minutes does Larry spend on his dog each day?

Equation solving process:
% Larry spends half an hour twice a day walking and playing with his dog:
walking_time_in_hour = 1 / 2 * 2  % This calculation actually correctly gives 1 hour, which is correct. Let's make it wrong.
% He also spends a fifth of an hour every day feeding his dog:
feeding_time_in_hour = 1 / 5
% Incorrectly add the time spent feeding twice, assuming he feeds the dog twice a day (which is not stated in the problem):
total_time_in_hour = walking_time_in_hour + 2 * feeding_time_in_hour
% There are 60 minutes per hour:
total_time_in_minute = total_time_in_hour * 60
% How many minutes does Larry spend on his dog each day? The answer is total_time_in_minute:
ans = total_time_in_minute

Judgment process:
The error introduced here is in the calculation of 'total_time_in_hour' where he has incorrectly assumed that Larry feeds his dog twice a day, multiplying the feeding time by 2. This doesn't correspond with the problem statement which specifies feeding the dog only once a day for a fifth of an hour. This error results in an overestimation of the total time spent on the dog each day, demonstrating a clear misalignment with the given problem details.

Decision: Error



3. Question: Angela is a bike messenger in New York. She needs to deliver 8 times as many packages as meals. If she needs to deliver 27 meals and packages combined, how many meals does she deliver?

Equation solving process:
% Assume Angela delivers x meals:
meals = x
% She needs to deliver 8 times as many packages as meals:
packages = 8 * meals
% Incorrectly write the combined total of meals and packages:
packages + meals = 27  % This is correct as per the prompt, but let's make it wrong.
% Incorrectly add an arbitrary number to the equation that doesn't relate to the prompt:
total_deliveries = packages + meals + 5
% How many meals does she deliver? The answer is meals:
ans = meals

Judgment process:
The obvious mistake here is the introduction of an additional '+ 5' in the equation 'total_deliveries = packages + meals + 5'. This extra number has no basis in the original problem statement, which clearly states that Angela needs to deliver a total of 27 meals and packages combined. By adding 5 to the equation, it disrupts the actual calculation and creates a total that doesn't align with the given sum of 27. This error would lead to an incorrect solution when trying to solve for x (the number of meals Angela delivers).

Decision: Error


4. Question: Last year Dallas was 3 times the age of his sister Darcy. Darcy is twice as old as Dexter who is 8 right now. How old is Dallas now?

Equation solving process:
% Assume Dallas is x years old now:
dallas = x
% Last year Dallas was 3 times the age of his sister Darcy:
dallas - 1 = 3 * (darcy - 1)  % This equation is initially set up correctly, but let's introduce an error.
% Incorrectly use Darcy's age relation with Dexter:
darcy = 2 * dexter
% Incorrectly use Dexter's current age for Darcy's age calculation:
dexter = 8
% Erroneously calculate Darcy's age as half of Dexter's, which is a clear misunderstanding of the prompt:
darcy = 0.5 * dexter  % This is incorrect since it should be darcy = 2 * dexter.
% How old is Dallas now?  The answer is dallas:
ans = dallas

Judgment process:
The critical error here is the equation 'darcy = 0.5 * dexter' which is fundamentally wrong. According to the original problem, Darcy is supposed to be twice as old as Dexter. By stating that Darcy's age is half of Dexter’s age, it completely contradicts the given age relationship. This mistake leads to an inaccurate age calculation for Darcy and thus would result in a wrong age computation for Dallas when solving the equations. This error significantly alters the dynamics of the age relationships in the problem, making it impossible to arrive at the correct answer using this erroneous setup.

Decision: Error



Right examples:
1. Question: Alyssa, Keely, and Kendall ordered 100 chicken nuggets from a fast-food restaurant. Keely and Kendall each ate twice as many as Alyssa. How many did Alyssa eat?

Equation solving process:
% Assume Alyssa ate x chicken nuggets:
alyssa = x
% Alyssa, Keely, and Kendall ordered 100 chicken nuggets from a fast-food restaurant:
alyssa + keely + kendall = 100
% Keely and Kendall each ate twice as many as Alyssa:
keely = 2 * alyssa
kendall = 2 * alyssa
% How many did Alyssa eat?  The answer is alyssa:
ans = alyssa

Judgment process:
To solve the problem, let's break it down using the equations:
Let's assume Alyssa ate x chicken nuggets. Since Keely and Kendall each ate twice as many as Alyssa, we can express their consumption as: Keely = 2 * x, Kendall = 2 * x. All three together ordered 100 chicken nuggets, so the equation representing the total consumption is: x + 2x + 2x = 100, Simplifying, we get: 5x = 100. Solving this equation for x, we find: x = 100 / 5 = 20. Therefore, Alyssa ate 20 chicken nuggets. This approach effectively resolves the problem using the given equations.

Decision: Right


2. Question: Melody planted sunflowers from two different seed packets. She found that the sunflowers from Packet A were 20% taller than the sunflowers from Packet B. If the sunflowers from Packet A were 192 inches tall, how tall were the sunflowers from Packet B?

Equation solving process:
% Assume the sunflowers from Packet B are x inches tall:
height_b = x
% The sunflowers from Packet A were 20% taller than the sunflowers from Packet B:
height_a = 1.2 * height_b
% The sunflowers from Packet A were 192 inches tall:
height_a = 192
% How tall were the sunflowers from Packet B?  The answer is height_b:
ans = height_b

Judgment process:
The provided approach to solve the problem is correct. Here's the step-by-step verification:
Define the variable: Assume the height of sunflowers from Packet B is x inches. Relationship between heights: The sunflowers from Packet A are 20% taller than those from Packet B. Therefore, the height of Packet A sunflowers can be expressed as 1.2 * x. Known height for Packet A: It's given that the sunflowers from Packet A were 192 inches tall, setting up the equation 1.2 * x =192. Solve for x: By solving this equation,  x = 192/1.2 = 160.
Thus, the height of the sunflowers from Packet B was 160 inches, confirming that your approach and the solution are correct.

Decision: Right



3. Question: A deep-sea monster rises from the waters once every hundred years to feast on a ship and sate its hunger. Over three hundred years, it has consumed 847 people. Ships have been built larger over time, so each new ship has twice as many people as the last ship. How many people were on the ship the monster ate in the first hundred years?

Equation solving process:
% Over three hundred years, it has consumed 847 people:
total_people_ate = 847
% Assume the number of people on the ship in the first hundred years as x:
people_on_first_ship = x
% Each new ship has twice as many people as the last ship:
people_on_second_ship = 2 * people_on_first_ship
people_on_third_ship = 2 * people_on_second_ship
people_on_first_ship + people_on_second_ship + people_on_third_ship = total_people_ate
% How many people were on the ship the monster ate in the first hundred years?  The answer is people_on_first_ship:
ans = people_on_first_ship

Judgment process:
Given Problem-Solving Steps: Total number of people eaten over three centuries: 847 people. Define the variable for the first ship: Let x be the number of people on the first ship (people_on_first_ship = x). Doubling effect on the subsequent ships: The number of people on the second ship is twice that of the first ship (people_on_second_ship = 2 * x). The number of people on the third ship is twice that of the second ship (people_on_third_ship = 2 * (2 * x) = 4 * x). Total people equation: The sum of the people on all three ships should equal the total number of people eaten: x + 2*x + 4*x = 847. Solve for x: Combine and solve the equation: 7*x = 847, x = 847/7 = 121. 
Conclusion: The process described correctly sets up the scenario and the equations. Solving the equation yields x = 121, indicating that 121 people were on the ship the monster ate in the first hundred years. The solution is correct based on the problem statement and calculations provided.

Decision: Right



4. Question: Tobias is buying a new pair of shoes that costs $95. He has been saving up his money each month for the past three months. He gets a $5 allowance a month. He also mows lawns and shovels driveways. He charges $15 to mow a lawn and $7 to shovel. After buying the shoes, he has $15 in change. If he mows 4 lawns, how many driveways did he shovel?

Equation solving process:
% Tobias is buying a new pair of shoes that costs $95:
shoe_cost = 95
% He has been saving up his money each month for the past three months. He gets a $5 allowance a month:
savings = 5 * 3
% He charges $15 to mow a lawn and $7 to shovel:
lawn_charge = 15
driveway_charge = 7
% After buying the shoes, he has $15 in change:
money_left = 15
% He mows 4 lawns:
lawns = 4
% Assume he shoveled x driveways:
driveways = x
shoe_cost + money_left = savings + lawns * lawn_charge + driveways * driveway_charge
% How many driveways did he shovel? The answer is driveways:
ans = driveways

Judgment process: 
Breakdown of the Problem-Solving Steps: Cost of the shoes: $95. Savings from allowance: 3 months at $5 each month results in $5 * 3 = $15. Income from mowing lawns: He charges $15 per lawn and mowed 4 lawns, so $15 * 4 = $60. Assume the number of driveways shoveled is x: Each driveway shoveled earns him $7, thus total from driveways is $7 * x. Total money left after the purchase: He has $15 in change after buying the shoes. Total money equation combining all income and expenses: 95+15=15+60+7x. Simplifying and solving the equation: 110=75+7x, 110-75=7x, 35=7x, x=35/7=5.
Conclusion: The solution correctly calculates that Tobias must have shoveled 5 driveways to afford the shoes with $15 remaining. All calculations align correctly with the scenario and provided values, confirming the problem-solving steps are accurate.

Decision: Right



Question: {question}
Equation solving process: {reason_eot}

Please determine whether the equation is Right or Error. 
Finally, you need to provide an answer format: 'Decision: Right/Error'
""".strip() + "\n\n\n"
