This is a _Markdown_ file with a bunch of tasks in it.

I think the [Github tasklists](https://docs.github.com/en/issues/tracking-your-work-with-issues/about-tasklists) have the simplest syntax 

- [ ] This is a Github-style task that needs action dtstamp:2023-06-23
- [x] This is a Github-style completed task dtstamp:2023-06-23

Especially if extended with the statuses described here https://xit.jotaen.net/.

- [~] This is an obsolete task dtstamp:2023-06-23

As a developer I've also used keyword based syntax like in [Org Mode](https://orgmode.org/manual/TODO-Items.html) so why not support that as well :

- TODO this is a keyword-style task that needs action dtstamp:2023-06-23
- DONE this is a keyword-style completed task dtstamp:2023-06-23

And since we've already expanded the syntax, why not also support the [todo.txt format](https://github.com/todotxt/todo.txt) :

- x (A) 2023-06-23 2023-06-01 this is a todo.txt-style completed task. dtstamp:2023-06-23
- (A) 2023-06-23 2023-06-01 this is a todo.txt-style task. dtstamp:2023-06-23
- 2023-06-23 this is a todo.txt-style task, we need a date at least (otherwise this is a plain list item). dtstamp:2023-06-23

And once we've made that step, why not also support hybrid formats :

- [x] 2023-06-01 this is a mixed-style task created on June 1st. dtstamp:2023-06-23
- [x] 2023-06-23 2023-06-01 this is a mixed-style task created on June 1st and completed on June 23rd. dtstamp:2023-06-23
- [ ] 2023-06-23 2023-06-01 this is a mixed-style task that can be correctly parsed but has **wrong** syntax (it has a completion date but it's marked as incomplete). dtstamp:2023-06-23
