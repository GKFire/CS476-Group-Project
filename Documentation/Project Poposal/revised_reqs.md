Done by Korbin Wyssen and Nicholas Fuzesy

## Lender Role
### Functional Requirements

**Create personal library**: The lender must have the ability to create a personal library
**Add items**: The lender must have the ability to add an item to their personal library
**Edit item**: The lender must have the ability to edit an item already in their personal library
**Remove item**: The lender must have the ability to remove an item from their personal library
**Mark item**: The lender must have the ability to mark an item as available or unavailable for borrowing
**Notify new request**: The system should notify the lender of new borrow requests
**Accept borrow request**: The lender must have the ability to accept a borrow request
**Decline borrow request**: The lender must have the ability to decline a borrow request
**Set return date**: The lender must have the ability to set/confirm a return date
**Show borrowed**: The lender must have the ability to see which items they own are currently being borrowed, and by whom
**Mark returned item**: The lender must have the ability to mark an item as returned
**Notify overdue item**: The system should notify the lender of overdue items

### Quality Requirements
Correctness:
- The request notification from the borrower must be correct
- An item entry’s information must be correct to what the lender set

Robustness:
- The system must show an error message if the lender attempts to set the return date to before the borrowing start date
- The system must show an error message if the lender attempts to private an item while the item is currently on loan

Time Efficiency:
- The system must take no longer than 2 seconds to redirect the lender to the item view page
- The system must take no longer than 5 seconds to list all items in the lender's personal library

## Borrower Role
### Functional Requirements

**View personal library**: The borrower must have the ability to view a lender's personal library
**See available items**: The borrower must have the ability to see items that are available to be borrowed
**Create Request**: The borrower must have the ability to make a request for an item from a lender
**Suggest Return Date**: suggest a return date in the request.
**Show borrowing**: The borrower must have the ability to what items they are currently borrowing, and from whom

### Quality Requirements
Correctness:
- The request response notification from the lender must be correct
- Borrower must not be able to see hidden (not whitelisted/blacklisted) items in a lender's personal library

Robustness:
- The system must show an error message when a borrower attempts to request an item already being borrowed
- The system must show an error message when a borrower attempts to access an item’s page that is not avaliable to them (the item is either blacklisted or not whitelisted for borrowing by the lender)

Time Efficiency:
- The system should take no longer than 3 seconds to show the borrower's borrowed items history
- The system should take no longer than 5 seconds to show results to a item search query
