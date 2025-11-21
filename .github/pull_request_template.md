# DQL-\<NUM\>: \<TITLE\>
`<DESCRIPTION>`

## :white_check_mark: Pre-Merge Checklist
All boxes must be checked before the Pull Request is merged. This checklist has to be completed by the reviewer.

- [X] The CI pipeline has passed (this is enforced by GitHub)
- [ ] Code Review
    - [ ] The code has been manually inspected by someone who did not implement the feature
- [ ] The PR implements what is described in the JIRA-Issue
- [ ] The new feature has been tested by the reviewer on his local machine
- [ ] A deployment to the `dev` environment has succeeded. If possible, ensure that the feature can be observed on the server.
- [ ] If required, any documentation is updated accordingly
- [ ] Valuable CI tests are implemented for all new code 

## :floppy_disk: Merge Checklist
- [ ] The branch is merged to main using the "Squash and Merge" strategy, following the commit message naming convention `DQL-<NUM>: <TITLE>`
- [ ] The branch is deleted after the PR is merged
