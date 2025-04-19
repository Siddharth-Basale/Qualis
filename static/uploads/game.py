import random

def play_game():
    possibilities = ["rock", "paper", "scissors"]
    computer_choice = random.choice(possibilities)

    user_choice = input("Enter your choice (rock, paper, or scissors): ").lower()

    if user_choice not in possibilities:
        print("Invalid choice. Please choose rock, paper, or scissors.")
        return

    print("\nYou chose: " + user_choice)
    print("Computer chose: " + computer_choice + "\n")

    if user_choice == computer_choice:
        print("It's a tie!")
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "paper" and computer_choice == "rock") or \
         (user_choice == "scissors" and computer_choice == "paper"):
        print("You win!")
    else:
        print("You lose!")

if __name__ == "__main__":
    play_game()
