
function reverse_word(string word):
    reversed = ""
    for letter in word:
        reversed = letter + reversed
    return reversed

function check_all_palindromes(array arr):
    if arr[0] == reverse_word(arr[0])
        if arr[1] == reverse_word(arr[1])
        if arr[2] == reverse_word(arr[2])

            return true

    return false


function reverse_word(string word):
    reversed = ""
    for letter in word:
        reversed = letter + reversed
    return reversed

function is_palindrome(string word):
    return word == reverse_word(word)

function check_all_palindromes(array arr):
    for word in arr:
        if is_palindrome(word) == false
            return false

    return true

