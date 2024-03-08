### Automate the deployment of markdown content as a static website to cloud based infrastructure ###

This application will help publish your [markdown](https://en.wikipedia.org/wiki/Markdown)
pages as a static website built with javascript and HTML effortlessly. Really
at the click of a file. All you need are:

- An Amazon account (access key and secret key)

- A git repository where your site content is.

- A domain name (e.g _www.my-cool-website.com_) - optional

Caveat: _You need to have [docker](https://www.docker.com/) installed._

For more information on what `markdown` is, scroll to the `markdown` section below

### Building ###

On first use build the docker image by running:

```shell
docker build -t poshjosh/automate-jamstack .
```

### Direct Usage ###

To create a new blog named `my-awesome-blog`:

- Create a properties file in the `/app/sites` directory. The file should be named
after the name of the site you are creating `my-awesome-blog.env`.

```
  └───app/
      └───sites/
          └───my-awesome-blog.env
```

- Site names are restricted 63 chars of lowercase letters, digits, periods and hyphens.

- Copy contents of `/app/config/site-data/default-properties.properties` into
the properties file (`/app/sites/my-awesome-blog.env`) you just created.

- Edit/Update the relevant properties in your properties file (`/app/sites/my-awesome-blog.env`).

- You need to provide values for at least these properties:

```dotenv
AWS_ACCESS_KEY=[VALUE REQUIRED]
AWS_SECRET_KEY=[VALUE REQUIRED]
AWS_REGION=[VALUE REQUIRED]
# E.g. https://github.com/[github-user]/[github-repository]/archive/master.zip
SITE_PAGES_SOURCE=[VALUE REQUIRED]
# E.g. git+https://github.com/[github-user]/[github-repository].git
SITE_REPOSITORY_URL=[VALUE REQUIRED]
```

- From the above, you need a public git repository, from where your site content will be pulled.

- Now you are ready to get going. Just open a terminal/command prompt and
run this script: `scripts/quick-run.sh`

### Customizations ###

Your site content is hosted in a git repository.

#### Assets ####

Place assets in an assets directory at the root of your site. E.g:

```
my-awesome-blog/
└───assets/
    └───banner.jpg
    └───icon.png
```
__Icon__

After adding an icon to your sites assets directory, specify the location of the
icon in the properties file of your site. Note that the location is relative to
the `SITE_PAGES_DIR` (i.e. `content/blog`) directory. E.g:

```dotenv
SITE_ICON_LOCATION=content/blog/assets/icon.png
SITE_PAGES_DIR=/content/blog
```

__Banner__

You can specify a banner for your site. Simply place either a
`banner.jpg` or `banner.png` image in the `assets` directory at
the root directory of your site.

### Deploying to Amazon S3 ###

- Change the profile property in the `/app/sites/my-awesome-blog.env` file you created earlier
from `PROFILE=dev` to production `PROFILE=prod`

- Run the app (See below for how to)

### Use a custom domain name ###

_This section only applies if you wish to use a custom domain name. Otherwise
skip to the next section_

If you wish to use a custom domain name e.g `my-awesome-blog` rather than
amazon allocated domain name e.g `<bucket-name>.s3-website.<region>.amazonaws.com`
then:

- Use your custom domain name as a bucket name e.g `my-awesome-blog.com`

- Login to amazon Route53

- Create a hosted zone with the name of the domain/bucket (e.g `my-awesome-blog.com`) and take 
note of the ID of the newly created hosted zone. Also take note of all the name servers.
E.g `ns-131.awsdns-16.com`

- Copy your name servers and use them to update the nameservers of your
domain service. The service where you purchased your domain name `my-awesome-blog.com`

- Run the app

### Run the app ###

- Open a terminal/command prompt and run this script: `scripts/quick-run.sh`
- It could take a while. Wait till you see a message like: `You can now view [Site Name] in the browser.`
- Browse to http://localhost:8000 to view you website on your local machine.

If your browser complains with an error message like the following. You may need
to relax any restrictions you switch on in the browser, particularly regarding javascript.
Otherwise, try other browsers.

```
Failed to get service worker registration(s): Storage access is restricted in this context due to user settings or private browsing mode. app.js:41
[HMR] connected client.js:95
SecurityError: The operation is insecure. app.js:41
404 page could not be found. Checkout https://www.gatsbyjs.org/docs/add-404-page/ index.js:2177
    __stack_frame_overlay_proxy_console__ index.js:2177
    loadPageDataJson dev-loader.js:28
```    

I set tough privacy restrictions on my firefox and go the above error. So I opened another
browser (microsoft Edge) and ```Hello World``` was displayed

- After basking in your first success. Take time out to read the advanced section
below.  

- For useful links, see the reference section at the end of the page

### Tips for writing blog content ###

This application will help publish your [markdown](https://en.wikipedia.org/wiki/Markdown)
pages as a static website built with javascript and HTML.

### What is Markdown ###

[Markdown](https://en.wikipedia.org/wiki/Markdown) is a markup language written
in plain text format. It allows you to add structure and style to your content
with more ease than permissible with html (another markup language). Markdown
is a format of writing. Markdown files end with `.md`. [Click here for some
common markdown](https://commonmark.org/help/)

Well composed markdown documents contain front matter.

### Frontmatter ###

- Add `frontmatter` at the topmost of all your pages. `Frontmatter` starts with
a single line of 3 hyphens `---` and ends with same. Example of `frontmatter`

```
---
path: "./README.md"
date: "2019-11-11"
title: "README"
description: "Usage instructions"
lang: "en-us"
tags: ["readme", "usage instructions", "useful info"]
---
```

- If you don't add frontmatter, one will be automatically generated for you.

- If you don't specify a title in frontmatter, article file names will be 
used as titles. In that case, dashes (-) will be replaced with spaces ( ). 
Two consecutive dashes or underscores will be treated as ( - ). For example:
`Abc-def,_ghi--jkl` will be converted to: `Abc def, ghi - jkl`

### Linking to other markdown ####

```
  └───blog/
      └───2010/
      │   │─  page1.md
      │   └─  page2.md
      │
      └───2011/
          └─  page3.md
```

Given the above structure, to link to `/blog/2011/page3.md` from
`/blog/2010/page1.md` simply enter `/blog/2011/page3`. No `.md` extension.

__Correct__

- `/blog/2011/page3`

__Wrong__

- `/blog/2011/page3.md`    <- .md
- `./blog/2011/page3`      <- single preceding dot
- `blog/2011/page3.md`     <- no preceding forward slash and .md
- `../blog/2011/page3`     <- double preceding dots

### Markdown Foot Notes ###

Standard Markdown doesn't support footnotes, but you can manually add footnotes
with superscript tags, e.g. <sup>1</sup>.

You can make the footnote links clickable as well.

- First define the footnote at the bottom like this

```
<a name="myfootnote1">1</a>: Footnote content goes here
```

- Then reference it at some other place in the document like this

```
<sup>[1](#myfootnote1)</sup>
```

### Converting between page formats ###

[Pandoc](https://pandoc.org/) is a command-line utility that can convert between various formats. It is available for Windows, Mac, and Linux. 

First [install Pandoc](https://pandoc.org/installing.html). Then use it to convert between formats.

Run the script `scripts/convert-to-markdown.sh` to convert multiple files to markdown.

__Example Pandoc Direct Usage__

Run the following command to convert a file called `doc.html` from html to markdown as file `doc.md`:

```shell
pandoc --standalone --from html --to markdown -o doc.md doc.html
```


### For more advanced users ###

The following steps will help you customize the website.

- Rename you markdown (pages having extension `.md`) pages to `sites/default-site/content/blog`

- Do not paste any `index.html` page as it will be auto generated for you. Pasting an index
page could interfer with the auto - generation process

- Rename any picture of yourself to `profile-pic.jpg` and place it in the
`sites/default-site/content/blog` directory, replacing any `profile-pic.jpg` therein.

- Rename you site icon to `site-icon.png` and place it in the `sites/default-site/content/assets` directory replacing any `site-icon.png` therein.

- To add styles do the following:

  ```
    └───src/
        └───components/
        │   │─  layout.js
  +     │   └─  layout.css   <-- Add this file here
        │
        └───pages/
            └─  index.js
  ```
  - Add a layout.css in the `sites/default-site/src/components` directory.

  - Import the layout into the `sites/default-site/src/components/layout.js` by
  adding `import "./layout.css"` to the top of `layout.js`

  - Enter styles to the `sites/default-site/src/components/layout.css` file e.g:

```
  div {
      background: #eeeeee;
      color: navy;
  }
```

- Take styling a step further by changing the typography (call it theme if you like)
of your website. [Click here](https://kyleamathews.github.io/typography.js/) to find
a selection of typography. To change the typography open file at
`sites/default-site/src/utils/typography.js` and change
`import Theme from "typography-theme-twin-peaks"` to any of the following:

```
  import Theme from "typography-theme-twin-peaks"
  import Theme from "typography-theme-lincoln"
  import Theme from "typography-theme-wordpress-2016"
  import Theme from "typography-theme-fairy-gates"
  import Theme from "typography-theme-grand-view"
```

- If you want to get your hands dirty with HTML, JavaScript, React, Graphql

  - Auto bio - `sites/default-site/src/components/bio.js`

  - Page layout - `sites/default-site/src/components/layout.js`

  - Blog post template - `sites/default-site/src/templates/blog-post.js`

### Some properties and their effects ###

VERBOSE - Causes a more verbose log

### Known Errors and Solutions ###

__Missing Field__

- __Example error message:__ `Cannot query field "tags" on type "MarkdownRemarkFrontmatter".`
- __Solution:__ Ensure at least one markdown page has the tags field in their frontmatter.

__Logs Enabled__

- __Example error message:__ `Error: creating Amazon S3 (Simple Storage) Bucket (logs): BucketAlreadyExists`
- __Solution:__ We currently set `logs_enabled` to `false` in `main.tf`.
```shell 
 Error: creating Amazon S3 (Simple Storage) Bucket (logs): BucketAlreadyExists: The requested bucket name is not available. The bucket namespace is shared by all users of the system. Please select a different name and try again.
       status code: 409, request id: 8BP9ZWJ7YED51GZG, host id: dhcmOr7XXc9cZuDYyiUTHqbZAC7wxNtH/6fBVwvGIZwJvoW+dxlEqNrwxzagGQkEAp1KzDXTIz/eZO/qpe9v1w==
 
   with module.s3_website.module.logs.module.aws_s3_bucket.aws_s3_bucket.default[0],
   on .terraform/modules/s3_website.logs.aws_s3_bucket/main.tf line 29, in resource "aws_s3_bucket" "default":
   29: resource "aws_s3_bucket" "default" {
```

### References ###

Markdown

- [Wikipedia - Markdown](https://en.wikipedia.org/wiki/Markdown)

- [Commonmark.org](https://commonmark.org/help/)

Gatsby

- [Gatsbyjs - Add global CSS](https://www.gatsbyjs.org/docs/global-css/)

- [Gatsbyjs - Deploying to Amazon S3](https://www.gatsbyjs.org/docs/deploying-to-s3-cloudfront/)

- [Gatsbyjs - Quck start](https://www.gatsbyjs.org/docs/quick-start/)

- [Gatsbyjs - Tutorial](https://www.gatsbyjs.org/tutorial/part-zero/)

Terraform

- [Terraform - AWS S3 Bucket](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html)

- [Terraform - Module S3 Bucket](https://github.com/terraform-aws-modules/terraform-aws-s3-bucket)

- [Cloudposse - Terraform Module for AWS S3 Website](https://github.com/cloudposse/terraform-aws-s3-website)

- [](https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/1.6.0)

AWS S3

- [AWS - Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html)

- [AWS - Guide to Static Web Hosting](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/static-website-hosting.html)

- [AWS - Getting Started with Static Websites](https://aws.amazon.com/getting-started/hands-on/host-static-website/)

- [AWS Policy Generator](https://awspolicygen.s3.amazonaws.com/policygen.html)

- [AWS - Secure S3 Resources](https://aws.amazon.com/premiumsupport/knowledge-center/secure-s3-resources/)
