A super-tiny utility that converts your todo.md file into an iCalendar file. The todo syntax is a super-set of Github styled tasklists, inspired by todo.txt and other related projects. Check out the example file in tests/todo.md for examples.

You can convert your todo.md like this:

    pip install txt2ics
    python -m txt2ics convert todo.md

And you can also serve your todo.md with HTTP:

    pip install txt2ics
    python -m txt2ics httpd todo.md

Related work (check the test file)

- Markwhen
- Todo.txt
