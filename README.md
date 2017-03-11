### API for automated testing of System Manager UI
Used tools:
- `Selenium WebDriver`
- `Python`

Given API is designed to perform automated UI testing of System Manager - web-based application for administrators of 
`FlashRay` all-flash array storage system. `System Manager` is built with using `Sencha`'s components, what allowed to 
build unified feature-rich components of API.

The core feature of API is wrapping of `WebDriver` web elements into API's `BaseComponent` class, and 
interacting with these "wrapped" elements rather than with `WebDriver` native elements. On dynamic web pages, references 
to web elements become "stale" on events such as element re-rendering or page reload, what causes raising 
`StaleElementReferenceException` when such an element referenced. `BaseComponent` class handles such situations by 
re-creating elements using their `XPath` selectors which are stored as class variables. This approach allows to avoid 
exception handling in multiple points across API and greatly improves testing reliability as if web elements never 
stale.

Web element locator strategy used in API is mentioned above `XPath` as it gives highest locating reliability when IDs 
of web elements are absent or dynamically generated, which was the case of application.

Besides interaction with elementary web elements API has next layer of abstraction represented by aggregated components 
of UI such as `Grid` (table) or `DropDownList`. In case of `Grid` user of API has ability, as example, of bulk selection 
of rows by certain criterion, or sorting table by specified column. Such operations involve complex logic and could 
hardly be performed at test scripting stage without using API.

Next layer of abstraction is `Page` (base or subclassed) representing collection of UI components on given page and some 
page-specific functions. This is implementation of `Page Object Model` design pattern.

Final layer of abstraction is so called `Wizard` (single or multi-page dialog) which allows to execute complex UI 
operations rather that interacting with separate components. 
