pipeline {
    agent any // This applies to the entire pipeline unless overridden by a stage

    environment {
        // Your Docker Hub username
        DOCKER_HUB_USERNAME = 'saleemkhandev'
        // Target server IP address for your EC2 instance
        TARGET_SERVER_IP = "122.248.206.50" // *** IMPORTANT: Double-check this IP is correct for your EC2 ***
        // This must match the ID you set for your SSH private key credential in Jenkins Credentials
        SSH_KEY_ID = "devops-target-server-ssh-key" // *** IMPORTANT: Verify this ID exactly matches your Jenkins credential ID ***
    }

    stages {
        // Jenkins automatically checks out the code configured in the job's SCM settings
        // at the very beginning of the pipeline run, so an explicit 'Checkout SCM' stage isn't needed.

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_HUB_USERNAME/simple-flask-app:latest .'
                }
            }
        }

        stage('Login to Docker Hub') {
            steps {
                // Uses a Jenkins 'Username with password' credential for Docker Hub
                withCredentials([usernamePassword(credentialsId: 'dockerhub-password-credential', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh 'docker push $DOCKER_HUB_USERNAME/simple-flask-app:latest'
                }
            }
        }

        stage('Deploy to EC2') {
            // This stage will run on the Jenkins master or any available agent.
            // This avoids issues with a specific 'saleem' agent being offline or the sshAgent step.
            agent any
            steps {
                script {
                    // This uses the 'sshCommand' step from the 'SSH Steps' plugin.
                    // Ensure the 'SSH Steps' plugin is installed in Jenkins.
                    sshCommand remote: [
                        host: env.TARGET_SERVER_IP,
                        user: 'ec2-user', // *** IMPORTANT: Change to 'ubuntu' if your EC2 instance is Ubuntu, or another username if applicable ***
                        credentialsId: env.SSH_KEY_ID,
                        allowAnyHosts: true // *** WARNING: For production, it's better to manage known_hosts for security. ***
                    ], command: """
                        set +e # Allow commands to fail without exiting the script immediately
                        
                        # Attempt to install Docker based on common Linux package managers
                        sudo yum install -y docker || sudo apt-get update && sudo apt-get install -y docker.io || true
                        
                        sudo systemctl start docker || true
                        sudo systemctl enable docker || true
                        
                        # Add current user (e.g., ec2-user or ubuntu) to the docker group to run docker commands without sudo
                        sudo usermod -a -G docker ec2-user || sudo usermod -a -G docker ubuntu || true # *** IMPORTANT: Adjust user here too ***
                        
                        set -e # Re-enable immediate exit on error for critical steps

                        # Stop and remove existing container and image to ensure a clean deployment
                        docker stop simple-flask-app-container || true
                        docker rm simple-flask-app-container || true
                        docker rmi ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest || true

                        # Pull the latest Docker image and run a new container
                        docker pull ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                        docker run -d -p 80:5000 --name simple-flask-app-container ${env.DOCKER_HUB_USERNAME}/simple-flask-app:latest
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs() // Clean up the workspace after the pipeline
        }
        failure {
            echo "Pipeline failed."
        }
        success {
            echo "Pipeline succeeded!"
        }
    }
}
