# sourdough

![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)
[![Build Status](https://img.shields.io/travis/with_precedent/sourdough.svg)](https://travis-ci.org/with_precedent/sourdough)

<em>"Sourdough is complicated and alive; it's fickle and mysterious; it's impossible and it's beautiful."</em> - [Sophie Lucido Johnson](https://www.bonappetit.com/story/sourdough-starter-love-letter)

<em>"Sourdough is basically an edible Tamagotchi."</em> - Meik Wiking

sourdough, true to its namesake, offers a starter base to complete a successful Python manager. It provides a set of classes embodying several core values:

* **Extensibility:** sourdough classes are designed to be easily expanded for a wide variety of applications. They avoid cluttering namespaces and subclasses with excess verbiage and use dunder (double underscore) methods and properties to avoid common conflicts with subclasses. Classes often include smart "add" methods to incorporate new options within the existing framework.
* **Accessibility:** While sourdough is usable by any level of python coder, it tries to ensure that it can be used by beginners. To that end, the package avoids programming jargon (when possible) and implements a consistent code architecture. Also, objects are always type annotated and include detailed documentation and comments.
* **Practicality:** sourdough is oriented toward common use cases where coders would need to implement tedious boilerplate and/or tricky solutions.
* **Flexibility:** Each class in sourdough can be used independently or collectively. Loose coupling is the norm, but hooks for subclass coordination are implemented as well. Mixins are included which allow easy implementation of features such as proxy naming of attributes and methods.

## Why sourdough?

**For beginners:** When I started out as a python coder, I spent a lot of time sifting through stackoverflow and reddit trying to find answers to specific implementation questions. While those online resources are great, particularly stackoverflow, they are not always easily searchable (if you don't know the exact wording for your problem) and accessible to newer programmers. So, I thought to put together some core classes that are more than design patterns, but less than full implementations to address common, often difficult, situations. But I didn't just want to offer cut-and-paste solutions - I felt it was important to make the code itself educational and illustrative. ssourdough code leans toward excessive verbosity with well-named variables and parameters. sourdough is basically a love letter to my past self, providing all the things that I wished I had when I started.

**For more advanced coders:** sourdough saves time and ensures consistency. Instead of reinventing the wheel each time, you can just import sourdough classes and subclass them. Particularly for often tedious techniques, like implementing a file management system for a manager, sourdough provides a base to easily adapt to specific scenarios. I will continue to use sourdough throughout my own work (e.g., [simplify](https://www.github.com/WithPrecedent/simplify)) to ensure it has value to those beyond beginning pythonistas.

## Why not sourdough?

sourdough is orientated toward offline, desktop manager design. Because I am an academic, that is the focus of my work and sourdough reflects that bias. That doesn't mean that sourdough classes can't be used in other situations - it just isn't designed specificially for those purposes. However, if you want to expand sourdough in another direction, [I welcome those contributions.](https://github.com/WithPrecedent/sourdough/contributors_guide.md)

sourdough takes advantage of some newer python features (dataclasses, __init_subclass__, ordered dictionaries, etc.) and is not compatible with versions of python before 3.7.

## What's in sourdough?

You can check out the [full documentation here.]()

Highlights of sourdough include:

* **Settings:** The Settings base class allows settings options to be set using a variety of file formats (py, json, ini) or a common python dictionary. It stores a mapping (dictionary) with a common, forgiving interface that allows settings to be easy shared, injected, or passed to different manager objects.
* **Workflow tracking:** The Project base class takes a list of stages (or a dictionary of stage names and methods) and tracks whether a corresponding method has been called. This makes it easy to check the state of the manager at any given moment and/or alter access methods according to the current stage of the manager.
* **File management:** The Filer base class and accompanying mixins make it easy to keep track of dynamic input and output file folders, file names, and file types. It incorporates appropriate packages to allow seamless transferring of files to and from disk and a variety of formats (csv, pickle, feather, hdf, json, excel, and png support is included).
* **Wilcard dictionary:** The Catalog class incorporates wildcard keys such as "default", "all", and "none" which return lists of values that match the wildcard keys. However, when seeking values from simple string keys, those are returned as would be by a normal python dictionary.
* **Lazy loading:** when including a wide variety of runtime options or strategies, it is often helpful to delay importation of packages and modules until they are needed. The LazyLoader class provides a flexible, forgiving way to implement runtime importation, particularly when importing many objects from a single package.
* **Dynamic, accessible pipeline objects:** Although there a lot of workflow pipeline options out there, many have difficult learning curves, require substantial overhead, or limit post-construction accessiblity. The last shortcoming arises largely because python dicitonaries do not store duplicate keys and lists are only accessible via index. The Worker class provides a clever way to pipeline objects that has the accessibility of a dictionary but allows duplicate "keys" like a list does. Because it behaves like a basic python type, it doesn't require any specialized coding or learning to use.

I always welcome suggestions and contributions to make sourdough better.
