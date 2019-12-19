

import pyodbc
from random import randint
import re

def searchListing(): 

    
    SQLCommand1 = ("SELECT DISTINCT L.id, L.name, L.number_of_bedrooms,") 
    SQLCommand2= (", LEFT(L.description, 25) FROM Listings L, Calendar C WHERE L.id=C.listing_id")
    print()

    ##########ASKS FOR DATE FIRST###
    dateString=''
    #USE regex to validate user input to be in the following format 
    r = re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2}')
    startDate= input("Enter check-in date (YYYY/MM/DD)\n")

    while not r.match(startDate): 
        startDate= input("Enter a PROPER check-in date (YYYY/MM/DD)\n")

    
    endDate= input("Enter check-out date (YYYY/MM/DD)\n")
    #validate correct input for check out date
    while not r.match(endDate): 
        endDate= input("Enter a PROPER check-out date (YYYY/MM/DD)\n")

    #Tail end of the string selects for listings available on every day listed by user 
    dateString= " AND C.date>="+"'"+startDate+"'"+" AND C.date<="+ "'"+endDate+"'"+" AND (SELECT COUNT(*) FROM Calendar D WHERE D.listing_id=L.id AND D.date>="+"'"+startDate+"'"+" AND D.date<="+ "'"+endDate+"'"+ ")=(SELECT COUNT(*) FROM Calendar E WHERE E.listing_id=L.id AND E.date>="+"'"+startDate+"'"+" AND E.date<="+ "'"+endDate+"'"+ "AND E.available=1)"


    ###USER CHOOSES FILTERS THEY WANT########### 

    while 1:
        filterInput= input("Enter 0 to show listings\nFilter Options:\n      1 to add minimum listing price\n      2 to add maximum listing price\n      3 to add number of bedrooms\n      5 to return to main menu")
        minPrice=0
        maxPrice=float("inf")
        bedroom=0
      
        minString=''
        maxString=''
        bedString=''
  
        while filterInput!='0':
            if filterInput=='5':
                return
            if filterInput=='1': 
                #use regex to validate user input as digits 
                r = re.compile('[0-9]')
                minPrice=input("Enter minimum listing price\n")
                while not r.match(minPrice):
                    minPrice=input("Enter a PROPER minimum listing price\n")
                # Find the min price in the date range using a subquery and compare with filter
                minString= " AND " +minPrice + "<=(SELECT MIN(Price) FROM Calendar C WHERE C.listing_id=L.id AND C.date>='"+startDate+ "' AND C.date<'"+endDate+"')"
                filterInput= input("Enter 0 to show listings\nFilter Options:\n      1 to update minimum listing price\n      2 to add maximum listing price\n      3 to add number of bedrooms\n      5 to return to main menu")
            
            elif filterInput=='2': 
                r = re.compile('[0-9]')
                maxPrice= input("Enter maximum listing price\n")
                #use regex to validate user input as digits 
                while not r.match(maxPrice):
                    maxPrice= input("Enter a PROPER maximum listing price\n")
                # Find the max price in the date range using a subquery and compare with filter
                maxString= " AND " +maxPrice + ">=(SELECT MAX(Price) FROM Calendar C WHERE C.listing_id=L.id AND C.date>='"+startDate+ "' AND C.date<'"+endDate+"')"

                filterInput= input("Enter 0 to show listings\nFilter Options:\n      1 to add minimum listing price\n      2 to update maximum listing price\n      3 to add number of bedrooms\n      5 to return to main menu")
            
            elif filterInput=='3': 
                r = re.compile('[0-9]')
                bedroom= input("Enter number of bedrooms\n")
                #use regex to validate user input as digits 
                while not r.match(bedroom):
                    bedroom= input("Enter a PROPER number of bedrooms\n")
                bedString= " AND L.number_of_bedrooms="+bedroom
                filterInput= input("Enter 0 to show listings\nFilter Options:\n      1 to add minimum listing price\n      2 to add maximum listing price\n      3 to update number of bedrooms\n      5 to return to main menu")


        #Query the total price of a listing in the date range 
        totalPrice="(SELECT SUM(F.price) total FROM Calendar F WHERE F.listing_id=L.id AND F.date>='"+startDate+ "' AND F.date<'"+endDate+"')"  
        
        #Concatenate all strings into final SQL query
        SQLCommand=SQLCommand1+totalPrice+SQLCommand2+minString+maxString+bedString+dateString
        print(SQLCommand)
        cur.execute(SQLCommand)
        results=cur.fetchone()
        
        #Check if search result is empty and prints an appropriate message
        if results==None: 
            print("Nothing was found. Try entering a valid input next time.")
            return
        while results:      
            print("Listing ID:" + str(results[0]))
            print("Name:" + str(results[1]))
            print("Number of bedrooms:" + str(results[2]))
            print("Total price:" + str(results[3]))
            print("Description(First 25 Characters):" + str(results[4]))
            print()
            results = cur.fetchone()    

        #Call Bookings Function if user wants to book one of the listings
        while 1:
            bookorno =input("Enter b to book a listing now or 5 to return to main menu") 
            if bookorno =='b':
                    bookListing()
            if bookorno =='5':
                return

#Function to generate a nonexistant, new listing_id in bookings 
def generateID():
    results= 1 
    #Checks if generated id is in use
    while results !=None: 
        random= randint(10000, 99999)
        SQLCommand = ("SELECT * FROM Bookings B WHERE B.id=?")
        cur.execute(SQLCommand, random)
        results=cur.fetchone()
    return random 

def bookListing():
    while 1: 
        bookingInput= input("Enter 0 to enter the booking information or 5 to return to the main menu")
        if bookingInput=='5': return 
        if bookingInput=='0':
            bookingID= generateID()
            listingID= int(input("Enter the Listing's ID:")) 
            guestName= input("Enter your name:")
            fromDate= input("Enter the check-in date (YYYY/MM/DD):")
            toDate= input("Enter the check-out date (YYYY/MM/DD):")
            numberGuests= int(input("Enter the number of guests:"))
            SQLCommand = ("INSERT INTO Bookings (id, listing_id, guest_name, stay_from, stay_to, number_of_guests) VALUES(?,?,?,?,?,?) ")
            Values=[bookingID,listingID,guestName,fromDate,toDate,numberGuests]
            #Process the query
            cur.execute(SQLCommand, Values)
            #Commit pending transaction 
            conn.commit()
            print("Booking confirmed! Book another place or go back to main menu.")
#Count the number of reviews to check if trigger was activated 
#i.e. no reviews are added if count is the same
def countReviews():
    SQLCommand = ("SELECT COUNT(*) FROM Reviews")
    cur.execute(SQLCommand)
    results=cur.fetchone()

    return results[0]

#Function  to generate  a new review id 
def generateRID():
    results= 1 
    while results !=None: 
        random= randint(100000, 999999)
        SQLCommand = ("SELECT * FROM Reviews R WHERE R.id=?")
        cur.execute(SQLCommand, random)
        results=cur.fetchone()
    return random 

def writeReview():
    while 1:
        reviewInput = input("Enter 0 to write a review or 5 to return to main menu")
        if reviewInput=='5': return 
        if reviewInput=='0':
            name = input("Enter your name because all guests have unique names =) :")
            SQLCommand = ("SELECT * FROM Bookings B WHERE B.guest_name=?")
            cur.execute(SQLCommand, name)
            results=cur.fetchone()

            #Prints out all the bookings for the guest to choose from
            while results: 
                print("Booking ID:" + str(results[0]))
                print("Listing ID:" + str(results[1]))
                print("Stay from:" + str(results[3]))
                print("Stay to:" + str(results[4]) +"\n")
                results = cur.fetchone()


            while 1: 
                reviewInput= int(input("Enter the booking id you would like to review or enter 5 to return: "))
                if reviewInput==5:break
                bookingID= reviewInput
                listingID=int(input("Enter the listing id of the booking: "))
                userName= input("Confirm your name again: ")
                #Check the number of reviews before to check if trigger was activated 
                countBefore = (countReviews())

            
                reviewText= input("Type your review here:  ")
                SQLCommand = ("INSERT INTO Reviews (listing_id, id, comments, guest_name) VALUES(?,?,?,?)")
                reviewID=generateRID()
                Values=[listingID, reviewID, reviewText, userName]
                cur.execute(SQLCommand, Values)
                #Commit pending transaction 
                conn.commit()

                #Check to see if the review count changed/ trigger was activated 
                countAfter =(countReviews()) 

                #If trigger activated: 
                if countAfter == countBefore:
                    print("Error: an SQL trigger was activated! No review was entered. You may only review after your check out date. You may only review if you booked the listing.")
                    return 
                else: 
                    print("Your review was successfully submitted! Thank you for your feedback!")

           
#Object containing SQL Server Connection
conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=USER;pwd=PASSWORD')
##########################
#Cursor creation 
cur = conn.cursor()
##########################
 
#Main Menu
print("Welcome to the Airbnb Main Menu!\n")
while 1: 
    command= input("Enter 1 to search and book a listing \n      3 to write a review")
    
    #Search Listings 
    if command=='1': 
        searchListing()
        
    #Book a Listing ONLY CALLED IN searchListing()
    # if command=='2':
    #     bookListing()

    if command=='3':
        writeReview()

conn.close()
