'''
    协程，又称微线程、纤程，英文名Coroutine。
    子程序，或者称为函数，在所有语言中都是层级调用，比如 A 调用 B，B 在执行的过程中又调用了 C，
    C 执行完返回 B，B 执行完返回 A，最后 A 执行完毕。
    所以子程序调用时通过栈实现的，一个线程就是执行一个子程序。
    子程序调用总是一个入口，一个返回(出口)，调用顺序是明确的。而协程的调用和子程序不同。
    协程看上去也是子程序，但执行过程中，在子程序内部可中断，然后转而执行别的子程序，在适当的时候再
    返回来继续执行。
    注意：在一个子程序中中断，去执行其他子程序，不是函数调用，而是有点类似 CPU 的中断。比如子程序 A、B：
        def A():
            print('1')
            print('2')
            print('3')
        def B():
            print('x')
            print('y')
            print('z')
    假设由协程执行，在执行 A 的过程中可以随时中断，去执行 B，B 也可能在执行的过程中中断再去执行 A，所以结果可能是：
        1
        2
        x
        y
        3
        z
    但是在 A中是没有调用 B 的，所以协程的调用比函数调用理解起来要难一些。
    
    看起来 A、B 的执行有点像多线程，但协程的特点在于是一个线程执行，那和多线程相比，协程有何优势呢？

    最大的效率就是协程的执行效率极高。因为子程序切换不是线程切换，而是由程序自身控制，因此，没有线程切换的开销，
    和多线程相比，线程数量越多，协程的性能优势就越明显。
    第二大优势就是不需要多线程的锁机制。因为只有一个线程，也就不存在同时写变量的冲突，在协程中控制共享资源不加锁，
    只需要判断状态就好了，所以执行效率比多线程高很多。
    因为协程是一个线程执行，那么如何利用多核 CPU 呢？最简单的方法是 多线程 + 协程，既充分利用多核，又充分发挥协程
    的高效率，可获得极高的性能。
    Python 对协程的支持是通过 generator 实现的。
    在 generator 中，我们不但可以通过 for 循环来迭代，还可以不断调用 next() 函数获取由 yield 语句返回的下一个值。
    但是 Python 的 yield 不但可以返回一个值，它还可以接收调用者发出的参数。
    e.g：
    传统的 生产者-消费者 模型是一个线程写消息，一个线程取消息，通过锁机制控制队列和等待，但一不小心就可能死锁。
    如果改用协程，生产者生产消息后，直接通过 yield 跳转到消费者开始执行，待消费者执行完毕后，切换回生产者继续生产，
    效率极高：
        def consumer():
            r = ''
            while True:
                n = yield r
                if not n:
                    return
                print('[CONSUMER] Consuming %s...' % n)
                r = '200 OK'
        
        def produce(c):
            c.send(None)
            n = 0
            while n < 5:
                n += 1
                print('[PRODUCER] Producing %s...' % n)
                r = c.send(n)
                print('[PRODUCER] Consumer return: %s' % r)
            c.close()
        
        c = consumer()
        produce(c)
    执行结果：
        [PRODUCER] Producing 1...
        [CONSUMER] Consuming 1...
        [PRODUCER] Consumer return: 200 OK
        [PRODUCER] Producing 2...
        [CONSUMER] Consuming 2...
        [PRODUCER] Consumer return: 200 OK
        [PRODUCER] Producing 3...
        [CONSUMER] Consuming 3...
        [PRODUCER] Consumer return: 200 OK
        [PRODUCER] Producing 4...
        [CONSUMER] Consuming 4...
        [PRODUCER] Consumer return: 200 OK
        [PRODUCER] Producing 5...
        [CONSUMER] Consuming 5...
        [PRODUCER] Consumer return: 200 OK
    注意到 consumer 函数是一个 generator ，把一个 consumer 传入 produce 后：
        1.首先调用 c.send(None) 启动生成器；
        2.然后，一旦生产了东西，通过 c.send(n) 切换到 consumer 执行；
        3.consumer 通过 yield 拿到消息，处理，又通过 yield 把结果传回；
        4.produce 拿到 consumer 处理的结果，继续生产下一条；
        5.produce 决定不生产了，通过 c.close() 关闭 consumer，整个过程结束。
    整个流程无锁，由一个线程执行,produce 和 consumer 协作完成任务，所以称作'协程'，而非线程的抢占式多任务。
'''
def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        r = '200 OK'

def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n += 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()

if __name__ == '__main__':
    c = consumer()
    produce(c)
