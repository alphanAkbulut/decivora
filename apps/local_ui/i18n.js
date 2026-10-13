/* Locale changes affect presentation only: no fetch, approval or model dispatch. */
window.DecivoraI18n = (()=>{
 const catalogs=window.DecivoraCatalogs,storageKey='decivora.ui.locale.v1';
 let locale='en';
 try{const saved=localStorage.getItem(storageKey);if(Object.hasOwn(catalogs,saved))locale=saved;}catch{}
 const t=(key,values={})=>{const text=catalogs[locale][key]??catalogs.en[key]??key;return text.replace(/\{(\w+)\}/g,(match,name)=>Object.hasOwn(values,name)?String(values[name]):match);};
 function apply(){document.documentElement.lang=locale;document.documentElement.dir=locale==='ar'?'rtl':'ltr';document.title=t('Decivora · Yerel çalışma alanı');
  for(const n of document.querySelectorAll('[data-i18n]'))n.textContent=t(n.dataset.i18n);
  for(const attr of ['placeholder','aria-label'])for(const n of document.querySelectorAll('[data-i18n-'+attr+']'))n.setAttribute(attr,t(n.getAttribute('data-i18n-'+attr)));
  document.getElementById('ui-language').value=locale;document.getElementById('ui-language').setAttribute('aria-label',t('Dil'));
 }
 function setLocale(value){locale=Object.hasOwn(catalogs,value)?value:'en';try{localStorage.setItem(storageKey,locale);}catch{}apply();}
 apply();return {t,setLocale,get locale(){return locale;}};
})();
