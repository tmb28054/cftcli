pipeline:
  agent: any

  options:
    - skipDefaultCheckout: true

  environment:
    - AWS_CREDENTIALS: credentials('AKIAR6EAZBPOYQFU67M2')
    - AWS_ACCESS_KEY_ID: ${AWS_CREDENTIALS_USR}
    - AWS_SECRET_ACCESS_KEY: ${AWS_CREDENTIALS_PSW}

  stages:
    - stage: Clean Workspace
      steps:
        - deleteDir

    - stage: Checkout
      steps:
        - checkout: scm

    - stage: Setup gci
      steps:
        - sh: aws sts get-caller-identity

    - stage: Setup Virtualenv
      steps:
        - sh: |
            python3 -m venv venv
            venv/bin/pip install --upgrade pip -q
            venv/bin/pip install . -q

    - stage: Run
      steps:
        - sh: venv/bin/secretmanager-env jenkins

  post:
    always:
      - deleteDir
