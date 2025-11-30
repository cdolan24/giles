We are building a web-scraper application that works as an extension to the University of California online library system. Provide infrastructure to expand coverage to other public digital scientific libraries.

The intention is not to duplicate data, but instead to be able to access it quickly. Only call upon data from the libraries provided. Each library should work like an MCP resource, something you can call upon quickly. 

**User Stories:**
The user should be able to inquire about a field of study (i.e. Quantum Computing) and be provided with links to the leading papers in the field, as well as recommended prerequisite knowledge. 
- Example: The user inquires about Calculus. You are able to provide the most comprehensive published book on the subject (rated the highest, referenced the most) as well as some papers to get you ready to read the text, such as a review of Algebra.

The user should be able to ask questions in a small chat window, ideally an extension.
- Example: After inquiring about Calculus, the user does not understand the concept of an integral. You can read the text in the book and recontextualize it using another reputable book from the provided libraries.

You will always cite your sources. Your purpose is not to restate the book, but instead to point the user in the right direction.
