# Java Poker Equity Simulator
This is a command-line and GUI-based Texas Hold'em poker equity simulator written in Java. It allows simulations between 2 to 10 players using random or user-specified hole and community cards.
Results are generated using Monte Carlo methods to estimate win probabilities and determine the best hand.

## Features

- Supports 2 to 10 players
- Random or manual input for hole cards and community cards (flop, turn)
- Hand strength evaluation: detects hand types and best 5-card combinations
- Monte Carlo simulation of thousands of poker hands per run
- Automatic prevention of duplicate cards via used-card tracking
- GUI version for user-friendly interaction

## Project Structure
- `PokerGUI.java` – Launches the graphical interface (main entry point)
- `PokerSimulation.java` – Handles simulations and CLI logic
- `Ranking.java` – Evaluates poker hands and determines winners
- `Deck.java` – Manages the card deck (shuffling, drawing, exclusions)
- PNG cards folder stores the card images used by the interface. 

