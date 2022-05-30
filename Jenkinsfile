pipeline{
    agent any
    environment{
        VERSION = "${env.BUILD_ID}"
    }
    stages{
        stage("Docker Build Push"){
            steps{
                script{
                     sh '''
                        ls
                        docker build -t registry.digitalocean.com/liquid-miners/lm-dev:${VERSION} .
                        docker push  registry.digitalocean.com/liquid-miners/lm-dev:${VERSION}
                        docker rmi registry.digitalocean.com/liquid-miners/lm-dev:${VERSION}
                    '''
                }
            }
        }
        stage('Deployment of Application on Kubernetes') {
            steps {
               script{
                   sh '''
                        kubectl set image deployment/lm-dev -n=default lm-dev=registry.digitalocean.com/liquid-miners/lm-dev:${VERSION}
                   '''
               }
            }
        }
    }
}