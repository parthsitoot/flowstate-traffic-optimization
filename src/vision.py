"""Classical CV: color segmentation and connected components on a synthetic camera frame.
No ground-truth boxes are passed to detect(). Real road footage needs a trained detector.
"""
import base64, struct, zlib
import numpy as np

def scene(queues):
    a = np.zeros((320,320,3), dtype=np.uint8)
    a[:] = [18,29,38]
    a[:,130:190] = [43,55,65]
    a[130:190,:] = [43,55,65]
    for d,count in enumerate(queues):
        for n in range(min(int(count),9)):
            lane, row = n%2, n//2
            if d == 0: x,y = 135+lane*25, 104-row*23
            elif d == 1: x,y = 198+row*23, 135+lane*25
            elif d == 2: x,y = 135+lane*25, 198+row*23
            else: x,y = 104-row*23, 135+lane*25
            w,h = (12,18) if d%2==0 else (18,12)
            a[y:y+h,x:x+w] = [80,195,230]
    return a

def detect(frame):
    mask = (frame[:,:,2] > 160) & (frame[:,:,1] > 120) & (frame[:,:,0] < 130)
    seen = np.zeros(mask.shape, bool)
    boxes, counts = [], [0]*4
    for y,x in zip(*np.where(mask)):
        if seen[y,x]: continue
        stack, points = [(int(y),int(x))], []
        seen[y,x] = True
        while stack:
            yy,xx = stack.pop(); points.append((yy,xx))
            for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
                if 0 <= ny < 320 and 0 <= nx < 320 and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx] = True; stack.append((ny,nx))
        if len(points) < 50: continue
        ys,xs = zip(*points); cx,cy = sum(xs)/len(xs),sum(ys)/len(ys)
        d = 0 if cy < 130 else 2 if cy >=190 else 3 if cx <130 else 1
        counts[d] += 1
        boxes.append({'x':min(xs),'y':min(ys),'w':max(xs)-min(xs)+1,'h':max(ys)-min(ys)+1,'direction':d})
    return boxes,counts

def png(a):
    def chunk(kind,data): return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    raw=b''.join(b'\0'+row.tobytes() for row in a)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',320,320,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')

def analyze(queues):
    frame=scene(queues); boxes,counts=detect(frame)
    return {'image':'data:image/png;base64,'+base64.b64encode(png(frame)).decode(), 'boxes':boxes,'counts':counts,
            'note':'Synthetic camera; visible capacity 9 vehicles per approach. Color segmentation, not a learned object detector.'}
