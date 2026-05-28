# yealookh

yealookh is a web application that generates dynamic SVG images of your selected GitHub repositories. It allows you to create a visually appealing list of your projects that can be seamlessly embedded into your GitHub Profile README or personal portfolio.

## Usage

1. Open the deployed yealookh application in your web browser https://yealookh.vercel.app.
2. Enter a GitHub username to fetch the user's public repositories.
3. Select the specific repositories you wish to showcase.
4. Click **Generate SVG URL**.
5. Copy the generated URL and embed it as an image in any Markdown file.

### Markdown Embedding Example

```markdown
## Selected Projects

![My Projects](https://yealookh.vercel.app/api/svg?user=forshaur&repos=yealookh,adyant,aarya)

```
![My Projects](https://yealookh.vercel.app/api/svg?user=forshaur&repos=yealookh,adyant,aarya)
