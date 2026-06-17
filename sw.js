/* ============================================================
   Service Worker — 组件素材缓存
   策略：Cache First（缓存优先），网络成功后更新缓存
   版本号变更即清旧缓存，确保素材更新时用户拿到新文件
   ============================================================ */

const CACHE_NAME = 'nunu-images-v15';

// 安装后立即激活，不等待其他标签页关闭
self.addEventListener('install', () => {
  self.skipWaiting();
});

// 激活后立即接管所有页面
self.addEventListener('activate', (event) => {
  event.waitUntil(
    clients.claim().then(() =>
      caches.keys().then((names) =>
        Promise.all(
          names.filter((n) => n.startsWith('nunu-images-') && n !== CACHE_NAME)
               .map((n) => caches.delete(n))
        )
      )
    )
  );
});

// 拦截请求：仅缓存 PNG 图片（组件素材 & 预览图）
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 只缓存同域 PNG 图片
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.endsWith('.png')) return;

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        // 缓存命中 → 立即返回；同时后台更新缓存
        const fetchPromise = fetch(request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        }).catch(() => null);
        return cached;
      }
      // 缓存未命中 → 网络请求 + 存入缓存
      return fetch(request).then((response) => {
        if (!response.ok) return response;
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        return response;
      });
    })
  );
});
