pipeline {
  agent any

  environment {
    // ID des credentials Jenkins (Secret Text) contenant votre token GitHub
    GIT_CRED = 'github-token'
    REPO_URL = 'https://github.com/MiloBonbaril/Assaisonnement_Interessant.git'
  }

  triggers {
    // Déclencheur à chaque push GitHub (nécessite webhook configuré)
    githubPush()
  }

  stages {
    stage('Checkout dev') {
      steps {
        // On force la branche dev
        checkout([$class: 'GitSCM',
          branches: [[name: '*/dev']],
          userRemoteConfigs: [[url: env.REPO_URL, credentialsId: env.GIT_CRED]]
        ])
      }
    }

    stage('Install & Tests') {
      steps {
        sh '''
          # Vérifions la version de Python
          python3 --version
          # Installation des dépendances (adaptez si requirements.txt diffère)
          pip install -r requirements.txt
          # Lancement des tests
          pytest --maxfail=1 --disable-warnings -q
        '''
      }
    }
  }

  post {
    success {
      // Si les tests passent, on pousse HEAD :main
      withCredentials([string(credentialsId: env.GIT_CRED, variable: 'TOKEN')]) {
        sh '''
          git config user.name "jenkins-bot"
          git config user.email "jenkins@example.com"
          git push https://$TOKEN@github.com/MiloBonbaril/Assaisonnement_Interessant.git HEAD:main
        '''
      }
    }

    always {
      // Quoi qu'il arrive, on repousse HEAD :dev pour rafraîchir la branche
      withCredentials([string(credentialsId: env.GIT_CRED, variable: 'TOKEN')]) {
        sh '''
          git config user.name "jenkins-bot"
          git config user.email "jenkins@example.com"
          git push https://$TOKEN@github.com/MiloBonbaril/Assaisonnement_Interessant.git HEAD:dev
        '''
      }
    }
  }
}
