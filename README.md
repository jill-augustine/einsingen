# Einsingen: An app for vocal warm-ups

Status: 👷 Work In Progress 

## Quickstart
In the terminal:
1. Clone the repo.
2. From the repo root run `docker compose up`

In the browser
1. Navigate to http://localhost:5173
2. Log in*
3. Select which musical patterns (scales, arpeggios etc.) to add to the Exercise Board
4. Reorder the patterns in the board if needed
5. Click "Load" to generate a musical exercise as a MIDI file
6. Click "Play" to play the exercise
7. (Optional) Click "Stop" to stop playback of the exercise

\* Currently users must be created directly on the backend using the django CLI. After creating a superuser, further users can be created via the backend api. See official [Django docs](https://docs.djangoproject.com).

## Troubleshooting
- Unable to authenicate using correct credentials?
    - Ensure your browser preferences do not block setting cookies using Set-Cookie. 

---
## Future Plans..., Wishes..., Dreams... 💭
### Now
- [x] feat: User can login via demo user
- [x] test: Backend unit tests
- [ ] ci: CI pipelines run tests
- [ ] feat: User can sign up
- [ ] feat: User can change password
- [ ] (maybe) fix: Requesting minor scale returns harmonic minor (to be confirmed)

### Next
- [ ] (maybe) test: pre-commit hooks installed and run linting, tests etc.
- [ ] feat: User can select arpeggios
- [ ] feat: User can select from library of Einsingen patterns (e.g. `1-2-1-2-3-2-1-2-3-4...`, or `1-8` skipping numbers with/without pitch)
- [ ] feat: User can view and reload previously created exercises (via an exercise history)
- [ ] feat: Version deployed on [jill.codes](https://jill.codes) uses custom theme colours
- [ ] feat: User can view app in dark mode based on user preferences (e.g. toggle button or defaults)
- [ ] refactor: Database is separated into separate service
- [ ] ci: CI pipelines run deployment of services
- [ ] feat: User sees formatted error page with themed background

### Later
- [ ] test: Frontend unit tests
- [ ] test: Integration tests?
- [ ] database service managed through Terraform
- [ ] feat: User can request password reset via email
- [ ] feat: User can watch visualisation of pattern during playback
- [ ] feat: User can randomise exercise generation
- [ ] feat: User can add tags to exercises for further filtering, e.g. during exercise randomisation

---
## Developer notes for debugging 🚫🪲🐛🪳⛔
* How to run midi files from CLI
```shell
fluidsynth -a coreaudio GeneralUser-GS.sf2 somefile.mid 
```

Soundfont can be downloaded from [GeneralUser-GS GitHub](https://github.com/mrbumpy409/GeneralUser-GS/raw/refs/heads/main/GeneralUser-GS.sf2).

