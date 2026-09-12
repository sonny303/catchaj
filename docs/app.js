'use strict';
const steps = [
  {name:'The Fact-Checker',symbol:'▤',title:'A good story starts\nwith the truth.',description:'Your resume becomes a shared Truth Document: the source every helper works from. Drafts are instructed to use only supported experience, numbers, and projects.',label:'THE WORKING RULE',example:'If it isn’t in the Truth Document, it doesn’t belong in the answer.',detail:'No invented achievements. No “synergy.” No inflated claims.',output:'A GROUNDED CANDIDATE PROFILE'},
  {name:'The Job Scout',symbol:'⌕',title:'Find possibilities.\nSkip the repeats.',description:'The discovery workflow searches job boards including LinkedIn and Indeed for healthcare product roles. It detects the application platform and deduplicates postings using company, title, and location.',label:'A FOCUSED SEARCH',example:'Senior healthcare product roles. One entry for each opportunity.',detail:'Discovery runs when invoked. Around-the-clock operation needs scheduling and monitoring.',output:'A DEDUPLICATED LIST OF ROLES'},
  {name:'The Strict Judge',symbol:'◎',title:'Your attention\nis worth protecting.',description:'The evaluator combines a 0–100 fit score with hard location and application-friction rules. Qualifying matches go to a Google Sheets tracker and trigger an email alert when the integrations are configured.',label:'THE BAR IS INTENTIONAL',example:'85+ for a straightforward application. 95+ when extra accounts get in the way.',detail:'A role outside the target location is rejected regardless of its match score.',output:'A SHORTLIST + AN ALERT'},
  {name:'The Essay Drafter',symbol:'✎',title:'Your experience.\nWith a better first draft.',description:'The drafting helper brings the role and candidate facts together to prepare concise application answers. The target is one or two useful paragraphs, supported by real projects and outcomes.',label:'THE EDITORIAL STANDARD',example:'Specific beats impressive-sounding. Every claim needs something real behind it.',detail:'AI-generated text is a draft. Review accuracy, relevance, and tone before using it.',output:'APPLICATION ANSWERS TO REVIEW'},
  {name:'The Browser Copilot',symbol:'↗',title:'The last click\nbelongs to you.',description:'A visible Chrome session opens the application and attempts to fill common fields, attach the resume, and add prepared text. Then it pauses for your review, edits, CAPTCHA, and final submission.',label:'THE HANDOFF',example:'“Your application is prepared. Take a look and submit when you’re ready.”',detail:'Form support varies. Browser staging is best-effort; the workflow does not click final Submit.',output:'A PREPARED FORM + HUMAN CONTROL'},
  {name:'The Privacy Guard',symbol:'◇',title:'Share the build.\nKeep the private bits.',description:'Private file exclusions and a pre-commit scanner help catch personal details and credentials before code is committed. A fictional Alex Morgan profile supports demos without using a real candidate’s information.',label:'SAFE DATA FOR A PUBLIC DEMO',example:'Meet Alex Morgan. A fictional candidate with a real purpose: testing the workflow.',detail:'These are safeguards against accidental sharing, not encryption or a complete privacy guarantee.',output:'SYNTHETIC EXAMPLES FOR TESTING'}
];
const tabs = [...document.querySelectorAll('[role="tab"]')];
function selectStep(index, focus = false) {
  const step = steps[index];
  tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; });
  document.getElementById('crew-panel').setAttribute('aria-labelledby', `tab-${index}`);
  const number = String(index + 1).padStart(2, '0');
  const values = {'step-kicker':`${number} / ${step.name.toUpperCase()}`,'step-symbol':step.symbol,'step-title':step.title,'step-description':step.description,'example-label':step.label,'step-example':step.example,'step-detail':step.detail,'step-output':`HANDOFF → ${step.output}`,'step-count':`${number} / 06`};
  Object.entries(values).forEach(([id,value]) => { document.getElementById(id).textContent = value; });
  document.getElementById('step-title').style.whiteSpace = 'pre-line';
  if (focus) tabs[index].focus();
}
tabs.forEach((tab,index) => {
  tab.addEventListener('click', () => selectStep(index));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectStep(next, true); }
  });
});
const scoreInput = document.getElementById('score');
const locationInput = document.getElementById('location');
const accountInput = document.getElementById('account');
function updateJudge() {
  const score = Number(scoreInput.value);
  const threshold = accountInput.checked ? 95 : 85;
  const locationPass = locationInput.checked;
  const qualifies = locationPass && score >= threshold;
  const scoreOutput = document.getElementById('score-value');
  scoreOutput.replaceChildren(document.createTextNode(String(score)));
  const denominator = document.createElement('span'); denominator.textContent = '/100'; scoreOutput.append(denominator);
  document.getElementById('demo-result').classList.toggle('rejected', !qualifies);
  document.getElementById('result-badge').textContent = qualifies ? 'WORTH A CLOSER LOOK' : 'YOUR TIME, PROTECTED';
  document.getElementById('result-icon').textContent = qualifies ? '↗' : '↳';
  document.getElementById('result-title').textContent = qualifies ? 'Make the shortlist.' : !locationPass ? 'Right role. Wrong place.' : accountInput.checked ? 'More friction. Higher bar.' : 'Keep looking.';
  document.getElementById('result-description').textContent = !locationPass ? 'The location is outside your target area. This role is filtered out, even with a perfect score. A match has to work for your life, too.' : qualifies ? `${score} clears the ${threshold}-point threshold, and the location fits. The workflow would log this role and send an alert.` : `A score of ${score} is below the ${threshold}-point threshold${accountInput.checked ? ' for an account-gated application' : ''}. This role stays off the shortlist, leaving your attention for a stronger fit.`;
  document.getElementById('location-check').textContent = locationPass ? 'PASS' : 'FAIL';
  document.getElementById('threshold').textContent = `${threshold} / 100`;
}
[scoreInput,locationInput,accountInput].forEach(input => input.addEventListener('input', updateJudge));
updateJudge();
