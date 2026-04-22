# Vibe Skills

This is a collection of skills that I have written or adapted, for
making life easier and better in [Mistral
Vibe](https://mistral.ai/products/vibe), the coding agent of
[Mistral](https://mistral.ai/).

My main goal is to have skills that help me during the development of
my personal projects. I typically use Rust, Python and Java for
this. Thus, the skills are more oriented towards these languages.

The development skills work together through the `kanban.db` SQLite3
database, which acts as a Kanban board for the development of a
project. As such it adds structure, persistence and transparancy to
the development process with a coding agent.

Do note: Mistral Vibe is still a coding agent, it might not always
follow the instructions of the skills and screw things up.

The aim of these skills is not to give you a set of agents to which
you say: "build me a Super Mario clone" and three days later your
clone is ready, more or less. 

The intent is to have skills that push back, document assumptions, ask
questions, give suggestions and in the end also do implementation
work. Thus consider this as a helpful set of assistant, which you tell
what to do, when to do and how to do things. They will (try to) behave
according to the instructions given.


---

# Example usage in Mistral Vibe

Do note: this will also work in other coding agents.

```
> / product-owner I want to build a task management system for tracking the state of my book.
> / architect Elaborate the tickets created by the product owner. 
> Implement the tickets discussed by the product owner and architect.
A whole lot of /compact and "yes please continue" later, a working application will appear.
```

---

# Product Owner

This skill turns ideas into initial structure and more detailed
information. This skill is instructed to note down assumptions it is
making. It needs to ask you questions to clarify your idea and what
direction you want to go in. Finally, it will write down a Product
Brief, and create tickets in `kanban.db`.

# Architect

This skill is instructed to architect simple architectures aimed at a
startup level software product. I.e., avoid unnecessary infrastructure
components for a small project (like load balancers, three different
types of databases, cloud lambda function integration, hyperscaling in
general, caching unless really needed, etc).

The architect will pick a technology (which typically will be React +
TypeScript + Node.js + Express + Webpack + Tailwinds), unless you have
specified that to the product owner. The architect should also explain
why it opts for these choices.

Finally, the architect will add technical elaboration to each ticket.

# Developer

TBC

# Refactor

I've copied this skill from
[Skills](https://skills.sh/github/awesome-copilot/refactor), which got
it from [Awesome CoPilot](https://github.com/github/awesome-copilot)
skills.

I mainly did reformatting.

