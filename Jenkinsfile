pipeline {
    agent any
    stages {
        stage('Run AWS CLI command') {
            steps {
                script {
                    withCredentials([
                        // Binds the credentials to environment variables for the enclosed steps
                        // The credentialsId is the ID you set in the Jenkins UI
                        // AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are the default variable names
                        [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'my-aws-creds']
                    ]) {
                        // Any 'sh' or 'script' step inside this block will have access to the variables
                        sh 'aws s3 ls' 
                    }
                }
            }
        }
    }
}
