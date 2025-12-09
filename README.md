# GitHub Pages 배포 가이드

이 프로젝트는 GitHub Pages를 통해 자동으로 배포됩니다.

## 배포된 사이트

🔗 **https://jennajeong627.github.io/LT_data_analysis/**

## 자동 배포

`main` 브랜치에 푸시하면 GitHub Actions가 자동으로 사이트를 배포합니다.

## 파일 구조

- `index.html` - 메인 진입점 (대시보드로 리다이렉트)
- `GT1_캠퍼스별_문항분석_대시보드.html` - 실제 대시보드
- `.github/workflows/deploy.yml` - GitHub Actions 워크플로우

## 로컬 개발

1. 대시보드 파일 수정
2. 변경사항 커밋 및 푸시:
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push origin main
   ```
3. GitHub Actions가 자동으로 배포 실행
4. 몇 분 후 배포된 사이트에서 확인

## 문제 해결

배포 상태는 GitHub 저장소의 **Actions** 탭에서 확인할 수 있습니다.
