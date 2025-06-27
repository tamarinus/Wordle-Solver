# Wordle-Solver
Dit project implementeert en vergelijkt twee algoritmes voor het oplossen van Nederlandse Wordle-puzzels: een naïeve methode en Monte Carlo Tree Search (MCTS).

# Installatie:
git clone https://github.com/tamarinus/Wordle-Solver.git
cd Wordle-Solver

# Gebruik:
1. Download wordle_woorden.txt of een eigen woordenlijst
2. Pas het pad aan: Verander pad= "pad_naar_woordenlijst.txt"
3. Run de code:
   woordenlijst = laad_woordenlijst(pad)

   ## voorbeelden:
   ### Test naïeve methode (100 spellen)
   evalueer("naief", woordenlijst, n=100)

   ### Test MCTS (100 spellen) 
   evalueer("mcts", woordenlijst, n=100)

   ### Test 1 spel met specifiek woord als geheim woord
   evalueer("naief", woordenlijst, n=1, geheim="hallo")

   ### MCTS met aangepast startwoord
   evalueer("mcts", woordenlijst, n=50, eerste_gok="schot")









Onderdeel van bacheloronderzoek Kunstmatige Intelligentie, Universiteit Utrecht (2025).

   

   
   
