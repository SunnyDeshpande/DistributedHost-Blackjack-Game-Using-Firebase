# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 18:40:28 2021

@author: sunny
"""

from libdw import pyrebase
import random, time

projectid = "<someprojectid>"
dburl = "<somedburl>"
authdomain = "<someauthdomain>"
apikey = "<someAPIkey>"
email = "<someemail@some.com>"
password = "<somepassword>" 

config = {
    "apiKey": apikey,
    "authDomain": authdomain,
    "databaseURL": dburl,
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password(email, password)
db = firebase.database()
user = auth.refresh(user['refreshToken']) 



playerdeck = []
scores = []
winners = []
playerstatus = []
playerhandlist = []
#values = ['2', '3', '4', '5', '6', '7'] 
suits = ['Diamonds', 'Clubs', 'Hearts', 'Spades']
values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] 
cardscore = 0
deckscore = 0
allscores = 0
turnnum = 1
host = False
start = False
win = False
lose = False
gameover = False
replay = False

def reset_database():
    db.child('start').set(False, user['idToken'])
    db.child('playerdetails').remove(user['idToken'])
    db.child('deck').remove(user['idToken'])
    db.child('turnindex').set(0, user['idToken'])
    db.child('playerscores').remove(user['idToken'])
    db.child('playerstatus').remove(user['idToken']) 
    db.child('playerskip').remove(user['idToken'])
    db.child('playerskip').child('placeholder').set(' ', user['idToken'])
    db.child('winners').remove(user['idToken'])
    db.child('gameover').set(False, user['idToken'])
    db.child('winnerslist').remove(user['idToken'])
    db.child('replay').remove(user['idToken'])
    db.child('replay').set('placeholder', user['idToken'])
    db.child('winners').remove(user['idToken'])

def create_deck(suits, values):
    deck = []
    
    for value in values:
        for suit in suits:
            deck.append([value, suit])
    return deck

def start_game(replay):
    players = 0
    host = False
    playername = input("Enter player name (ADMIN if first player): ")
    if(playername == 'ADMIN'):
        db.child('playercount').set(0, user['idToken'])
        playername = input("Game reset!\nEnter player name again: ")
        print(replay)
    if(replay == True):
        db.child('playercount').set(0, user['idToken'])
        print('Replay Host!')
        replay = False
    players = db.child('playercount').get(user['idToken']) .val()
    if players == 0: 
        host = True
        db.child('hostname').set(playername, user['idToken'])
    if (host == True):
        print('You are host!')
        reset_database()
        
    else:
        hostname = db.child('hostname').get(user['idToken']) .val()
        print(hostname + " is host!")
       
    db.child('playerdetails').child(playername).set('', user['idToken'])
    players += 1
    db.child('playercount').set(players, user['idToken'])
    return playername, host

def blackjack(replay, start, playerhandlist, turnnum, gameover, deckscore, scores, winners, playerdeck):
    while(1):
        playername, host = start_game(replay)
        win = False
        lose = False
        
        if (host == False):    
                print("Waiting for host to start the game...")        
    
        while(start == False):
            if (host == True):
                if input("Start game? (Y=Yes, N=No): ").upper() == 'Y':
                    start = True
                    db.child('start').set(start, user['idToken'])
            start = db.child('start').get(user['idToken']) .val()
                    
        print('Starting game! \nShuffling cards!')
        if host == True:
            deck = create_deck(suits, values)
            random.shuffle(deck)
            db.child('deck').set(deck, user['idToken'])
        
        playerlist = db.child('playerdetails').get(user['idToken']) .val()
        
        
        db.child('turn').set(list(playerlist.keys())[0], user['idToken'])
        turn = db.child('turn').get(user['idToken']) .val()
        
        db.child('playerstatus').child(playername).set('Playing', user['idToken'])
        
        
        while(turn!= playername):
            turn = db.child('turn').get(user['idToken']) .val()
            #print('Playername is: '+ playername + ' but turn is of: ' + turn)
    
        deck2 = db.child('deck').get(user['idToken']) .val()
        
        playerdeck.append(deck2.pop(0))
        playerdeck.append(deck2.pop(0))
        
        db.child('deck').remove(user['idToken'])
        db.child('deck').set(deck2, user['idToken'])
        for card in playerdeck:
            playerhandlist.append(" of ".join(card))
        print('Your deck is: ' + ", ".join(playerhandlist))
        playerhandlist = []
        
        
        #Takes care of turns in drawing cards
        turnindex = db.child('turnindex').get(user['idToken']) .val()
        #print(turnindex)
        turnindex+=1
        db.child('turnindex').set(turnindex, user['idToken'])
        if turnindex >= len(list(playerlist.keys())):
            turnindex = 0
            turnnum += 1
            db.child('turnnum').set(turnnum, user['idToken'])
        time.sleep(1)
        db.child('turn').set(list(playerlist.keys())[turnindex], user['idToken'])
        
        db.child('turnindex').set(turnindex, user['idToken'])
    
        
    
        while(gameover == False):
            
            #Check score of deck
            for card in playerdeck:
                try:
                    cardscore = int(card[0])
                except:
                    if(card[1] == 'A'):
                        if(playerdeck[0] == 'A'):
                            if(playerdeck.index(card) <= 1):
                                cardscore = 1
                        else:
                            cardscore = 11
                    else:
                        cardscore = 10
                #print(cardscore)
                deckscore += cardscore
            print("Your deck's total score is: " + str(deckscore) + '\n')
            db.child('playerscores').child(playername).set(deckscore, user['idToken'])
            
            #Check for win/lose
            if(deckscore > 21):
                lose = True
                print("You lose! (>21)")
                db.child('playerstatus').child(playername).set('Lose', user['idToken'])
            elif(deckscore == 21): 
                win = True
                print("You win!")
                db.child('playerstatus').child(playername).set('Win', user['idToken'])
                db.child('winners').set(playername, user['idToken'])
            deckscore = 0   
            turnindex = db.child('turnindex').get(user['idToken']).val()
            
            
            try:
                #If all three players skip
                if(len(list(db.child('playerskip').get(user['idToken']) .val().keys())) == len(list(playerlist.keys()))+1):
                    print('Everyone skipped!')
                    allscores = db.child('playerscores').get(user['idToken'])
                    for key in allscores.val():
                        if(allscores.val()[key] <= 21):
                            scores.append(allscores.val()[key]) 
                    max_value = max(scores)
                    for person in allscores.val():
                        if(allscores.val()[person] == max_value and allscores.val()[person] <= 21):
                            winners.append(person)
                    #winners = {key for key, value in allscores.items() if value == max_value}
                    print(winners)
                    db.child('winnerslist').set(winners, user['idToken'])
                    db.child('winners').set(winners, user['idToken'])
                    db.child('gameover').set(True, user['idToken'])
                
                playerstatus = []
                for key in db.child('playerstatus').get(user['idToken']) .val(): 
                    playerstatus.append(db.child('playerstatus').get(user['idToken']) .val()[key])
      
                #if somebody won by end of turn
                if(playerstatus.count('Win') >= 1):
                    print('Somebody got a blackjack!')
                    for key in db.child('playerstatus').get(user['idToken']).val():
                        if(db.child('playerstatus').get(user['idToken']).val()[key] == 'Win'):
                            winners.append(key)
                    #print(winners)
                    db.child('winnerslist').set(winners, user['idToken'])
                    db.child('gameover').set(True, user['idToken'])
                    
                elif(playerstatus.count('Lose') == len(list(playerlist.keys()))-1):
                    print('Only one player won!')
                    #allstatus = db.child('playerstatus').get(user['idToken']).val()
                    #winners = {key for key, value in allstatus.val() if value != 'Lose'}
                    
                    for key in db.child('playerstatus').get(user['idToken']).val():
                        if(db.child('playerstatus').get(user['idToken']).val()[key] != 'Lose'):
                            winners.append(key)
                    ####
                    db.child('winnerslist').set(winners, user['idToken'])
                    db.child('gameover').set(True, user['idToken'])
                    
            
                
                elif(playerstatus.count('Lose') == len(list(playerlist.keys()))):
                    print('Nobody won!')
                    #allstatus = db.child('playerstatus').get(user['idToken']).val()
                    #winners = {key for key, value in allstatus.val() if value != 'Lose'}
                    
                    #db.child('winnerlist').child(playername).set(winners, user['idToken'])
                    #SET ALL LOSE FLAG!
                    db.child('gameover').set(True, user['idToken'])
                      
            except:
                pass
            
            gameover = db.child('gameover').get(user['idToken']).val()
            if(gameover == True):
                print('Gameover!')
                break
            
            
            #Hold player in loop until turn
            turn = db.child('turn').get(user['idToken']) .val()
            print('Waiting for other players to complete their turn')
            while(turn!= playername):
               turn = db.child('turn').get(user['idToken']) .val()
               gameover = db.child('gameover').get(user['idToken']).val()           
               #print('Playername is: '+ playername + ' but turn is of: ' + turn)
               
            time.sleep(1)
            gameover = db.child('gameover').get(user['idToken']).val()
            #print('Turn ' + str(turnnum) + ':')
            #print(gameover)
            if(gameover == True):
                print('Game Over!')
                db.child('turn').set(list(playerlist.keys())[turnindex], user['idToken'])
                db.child('turnindex').set(turnindex, user['idToken'])
                break
            else:
                if(lose == False and win == False):
                    answer = input('Do you wish to draw? (Y=Yes, N=No): ').upper()
                    if (answer == 'Y'):
                        deck2 = db.child('deck').get(user['idToken']) .val()
                        
                        playerdeck.append(deck2.pop(0))
                        
                        db.child('deck').remove(user['idToken'])
                        db.child('deck').set(deck2, user['idToken'])
                        
                        for card in playerdeck:
                            playerhandlist.append(" of ".join(card))
                        print('Your deck is: ' + ", ".join(playerhandlist))
                        playerhandlist = []
                        
                        
                        db.child('playerskip').child(playername).remove(user['idToken'])
                    elif (answer == 'N'):
                        db.child('playerskip').child(playername).set('True', user['idToken'])
                elif(lose == True):
                    db.child('playerskip').child(playername).set('True', user['idToken'])
            
            #Takes care of turns in drawing cards----------------------------------
            
            #print(turnindex)
            if turnindex >= len(list(playerlist.keys())):
                turnindex = 0
                turnnum += 1
                db.child('turnnum').set(turnnum, user['idToken'])
            db.child('turn').set(list(playerlist.keys())[turnindex], user['idToken'])
            db.child('turnindex').set(turnindex, user['idToken'])
    
        winners = []
        if(type(db.child('winnerslist').get(user['idToken']).val()) == list):
            winners = db.child('winnerslist').get(user['idToken']).val()
        else:
            for key in db.child('winnerslist').get(user['idToken']).val():
                winners.append(db.child('winnerslist').get(user['idToken']).val()[key])    
        print('The winner(s) is/are: ')
        if (len(winners) > 0):
            print(", ".join(winners))
        else: 
            print('Nobody LMAOS')
        
        #Check for replay
        replay = input('Play Again? (Y=Yes, N=No): ').upper() 
        while(replay != 'Y' and replay != 'N' and replay != 'YES' and replay != 'NO'):
            print('Invalid entry')
            replay = input('Play Again? (Y=Yes, N=No): ').upper() 
        if (replay == 'Y' or replay == 'YES'):
            db.child('replay').child(playername).set(True, user['idToken'])
            print('Waiting for other players: ...')
        elif(replay == 'N' or replay == 'NO'):
            db.child('playerdetails').child(playername).remove(user['idToken'])
            break
            
        
        while(len(db.child('replay').get(user['idToken']).val()) != len(db.child('playerdetails').get(user['idToken']).val())):
           pass
        
        start = False
        db.child('start').set(start, user['idToken'])
        db.child('playercount').set(0, user['idToken'])
        playerdeck = []
        cardscore = 0
        deckscore = 0
        allscores = 0
        turnnum = 1
        host = False
        start = False
        gameover = False
        replay = False
        playerdeck = []
        scores = []
        winners = []
        playerstatus = []
        playerhandlist = []
    
blackjack(replay, start, playerhandlist, turnnum, gameover, deckscore, scores, winners, playerdeck)
    
    
    
    

    
    
    
  
###my_stream.close()

