# sourdough

![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)
[![Build Status](https://img.shields.io/travis/with_precedent/sourdough.svg)](https://travis-ci.org/with_precedent/sourdough)

<em>"Sourdough is complicated and alive; it's fickle and mysterious; it's impossible and it's beautiful."</em> - [Sophie Lucido Johnson](https://www.bonappetit.com/story/sourdough-starter-love-letter)

<em>"Sourdough is basically an edible Tamagotchi."</em> - [Meik Wiking](https://us.gozney.com/blogs/academy/how-to-make-a-sourdough-starter)

True to its namesake, sourdough offers a starter base to complete a Python project. It provides a framework and a set of classes embodying several core values:

* **Practicality:** sourdough is oriented toward common use cases where coders would need to implement tedious boilerplate and/or tricky solutions. sourdough provides easy-to-use classes and functions to replace the tedious parts of coding.
* **Flexibility:** Almost always, classes in sourdough can be used independently or collectively. Loose coupling is the norm, but hooks for subclass coordination are implemented as well. Mixins are included which allow easy implementation of features such as proxy naming of attributes and methods or registering subclasses and subclass instances.
* **Efficiency:** sourdough implements eager validation, but lazy evaluation (when possible). This means that datatypes are checked early to ensure errors are caught before a computationally expensive iteration begins, but objects are not imported or initialized until they are needed. This limits sourdough's overhead and memory consumption without compromising its functionality. 
* **Accessibility:** While sourdough is usable by any level of python coder, it tries to ensure that it can be used by beginners. To that end, the package avoids programming jargon (when possible) and implements a consistent code architecture. Also, within the sourdough code, classes, functions, and methods are always type annotated and include detailed documentation and comments. This level of verbosity will seem excessive to experienced programmers, but is part of sourdough's broad mission.
* **Extensibility:** sourdough classes are designed to be easily expanded for a wide variety of applications. They avoid cluttering namespaces and subclasses with excess verbiage and use dunder (double underscore) methods and properties to avoid common conflicts with subclasses. Classes often include smart "add" methods to incorporate new options within the existing framework. Specific instructions for subclassing, when needed, are included within the general API (Application Programming Interface) documentation for each sourdough class. sourdough also includes several wrapper classes and methods for incorporating other packages within the sourdough ecosystem and framework.


## Why sourdough?

**For beginners:** When I started out as a python coder, I spent a lot of time sifting through stackoverflow and reddit trying to find answers to specific implementation questions. While those online resources are great, particularly stackoverflow, they are often not easily searchable (if you don't know the exact wording for describing your problem) or accessible to newer programmers. So, I thought to put together some core classes that are more than design patterns, but less than full implementations to address common, often difficult, situations. But I didn't just want to offer cut-and-paste solutions in a black-box package - I felt it was important to make the code itself educational and illustrative. sourdough always uses clearly named variables and parameters. sourdough is basically a love letter to my past self, providing all the things that I wished I had when I started.

**For more advanced coders:** sourdough saves time and ensures consistency. Instead of reinventing the wheel each time you begin a project, you can just import sourdough classes, subclass them, or use the project subpackage. Particularly for often tedious techniques, like implementing a file management system for a project or designed a flexible system for configuration settings, sourdough provides a base to easily adapt to specific scenarios. I will continue to use sourdough throughout my own work (e.g., [simplify](https://www.github.com/WithPrecedent/simplify)) to ensure it has value to those beyond beginning pythonistas.

## Why not sourdough?

sourdough is orientated toward offline, desktop manager design. Because I am an academic, that is the focus of my work and sourdough reflects that bias. That doesn't mean that sourdough classes can't be used in other situations - it just isn't designed specificially for those purposes. However, if you want to expand sourdough in another direction, [I welcome those contributions.](https://github.com/WithPrecedent/sourdough/contributors_guide.md)

sourdough takes advantage of some newer python features (dataclasses, __init_subclass__, ordered dictionaries, etc.) and is not compatible with versions of python before 3.7.

## What's in sourdough?

You can check out the [full documentation here.](https://sourdough.readthedocs.io/en/latest/)

Highlights of sourdough include:

* **Easy configuration:** The Settings base class allows settings options to be set using a variety of file formats (py, json, ini, and toml) or a common python dictionary. It stores a dictionar) with a common, forgiving interface that allows settings to be easy shared, injected, or passed to different objects. Settings is easy integrated into any project, even ones not using the rest of the sourdough framework.
* **File management:** Filer and its related classes make it easy to keep track of dynamic input and output file folders, file names, and file types. It incorporates appropriate packages to allow seamless transferring of files to and from disk and a variety of formats (csv, pickle, feather, hdf, json, excel, and png are supported out-of-the-box). Like Settings, it can be used independently. But it also integrates with Settings classes and the overall sourdough framework.
* **Wilcard dictionary:** The Catalog class incorporates wildcard keys such as "default", "all", and "none" which return lists of values that match the wildcard keys. It can also accept a list of keys and return a list of matchign values. However, when seeking values from simple string keys, those are returned as would be by a normal python dictionary. Catalog is particularly useful when implementing different strategies or options at runtime.
* **Hybrid iterable:** The Hybrid class combines the functionality and interfaces of python dicts and lists. It allows duplicate keys and list-like iteration while supporting the easier access methods of dictionaries. Hybrids can also contain large composite structures that are easily traversed using its 'find' and 'apply' methods. In order to support this hybrid approach to iterables, Hybrid is limited to storing the lightweight, easily subclassed Component class.
* **Lazy loading:** when including a wide variety of runtime options or strategies, it is often helpful to delay importation of packages and modules until they are needed. The LoaderMixin provides a flexible, forgiving way to implement runtime importation, particularly when importing many objects from a single package. It can easily be added to any Component subclass as well as non-sourdough objects. Like all sourdough mixins, LoaderMixin includes a list of potential namespace conflicts in the documentation if you wish to use it outside of the sourdough framework.
* **Dynamic, accessible workflows:** Although there a lot of workflow pipeline options out there, many have difficult learning curves, require substantial overhead, or limit post-construction accessiblity. The last shortcoming arises largely because pipelines generally rely on python dicitonaries that do not store duplicate keys or lists that are only accessible via indexing. Aiding a Worker instance's transparency, at any moment, you can get an easy to understand snapshot of its stored objects using its 'overview' property. Further, Worker instances are very flexible and can incorporate a variety of structures and iterables using the sourdough Role subclasss. The Worker class expands on the Hybrid class, providing a clever way to make pipelines, graphs, trees, cycles, and other composite objects both transparent and functional. 

I always welcome suggestions and contributions to make sourdough better.
