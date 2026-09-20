# Blog Lab media upload – GitHub token permission fix

## Symptom

The private terminal shows this error when uploading a photo:

```text
Slike ni bilo mogoče shraniti v GitHub. GitHub token potrebuje Repository permission: Contents = Read and write. [GITHUB_CONTENTS_WRITE_REQUIRED]
```

## Meaning

This is not a broken image picker or drag-and-drop frontend issue. The Worker receives the image and then tries to save it through the GitHub Contents API into the repository media library, usually under:

```text
public/media/uploads/...
```

GitHub is rejecting that write request because the token stored in the Cloudflare Worker secret `GITHUB_DISPATCH_TOKEN` does not have repository content write permission for `DDAY2301/blog-lab`.

## Required token permissions

Create or update a GitHub fine-grained personal access token for repository:

```text
DDAY2301/blog-lab
```

Minimum repository permissions:

```text
Contents: Read and write
Metadata: Read-only
```

Recommended when the terminal also triggers GitHub Actions workflows:

```text
Actions: Read and write
Workflows: Read and write
```

Never commit this token to the repository and never paste it into chat.

## Cloudflare fix

From the Worker project folder, update the Cloudflare Worker secret:

```bash
npx wrangler secret put GITHUB_DISPATCH_TOKEN
npx wrangler deploy
```

Paste the token only into the Wrangler prompt or Cloudflare dashboard secret field.

## Verification

After deploy:

1. Open the private terminal.
2. Refresh the browser.
3. Upload one small JPG/PNG test image.
4. Confirm that a new file appears under `public/media/uploads/` in the GitHub repository.
5. Confirm that the terminal no longer shows `GITHUB_CONTENTS_WRITE_REQUIRED`.

## Why GitHub Actions alone is not enough

GitHub Actions workflow permissions such as `contents: write` only apply inside GitHub Actions jobs. The browser upload path runs through the Cloudflare Worker, so it depends on the Worker secret `GITHUB_DISPATCH_TOKEN`.
